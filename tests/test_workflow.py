"""Integration checks for the database rules and the local web interface.

Run only against a disposable, freshly seeded database named dbms_pbl_test_*.
"""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from uuid import uuid4

from app.db import fetch_one
from app.services import (
    RuleError,
    add_volunteer,
    assess_need,
    assign_volunteer,
    distribute,
    receive_donation,
)
from app.web import app


class WorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = os.environ.get("DB_NAME", "")
        if not name.startswith("dbms_pbl_test_"):
            raise RuntimeError("Set DB_NAME to a disposable database named dbms_pbl_test_*")

    def test_duplicate_assessment_is_rejected(self):
        with self.assertRaisesRegex(RuleError, "already has an assessment"):
            assess_need(1, 1, "2026-W01", 5, "HIGH")

    def test_concurrent_issues_cannot_exceed_need(self):
        need_id = assess_need(1, 1, "RACE-" + uuid4().hex[:8], 5, "HIGH")
        before = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=1")

        def try_issue():
            try:
                return distribute(need_id, 1, 1, 3, str(uuid4()))
            except RuleError as exc:
                return str(exc)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: try_issue(), range(2)))
        self.assertEqual(sum(isinstance(result, int) for result in results), 1)
        self.assertTrue(any("remaining assessed need" in str(result) for result in results))
        issued = fetch_one(
            "SELECT COALESCE(SUM(quantity_issued), 0) AS quantity FROM distributions WHERE need_id=%s",
            (need_id,),
        )["quantity"]
        after = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=1")
        self.assertEqual(issued, 3)
        self.assertEqual(after["quantity_on_hand"], before["quantity_on_hand"] - 3)

    def test_receipt_increases_stock_and_records_movement(self):
        before = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=3")
        token = str(uuid4())
        donation_id = receive_donation(1, 1, 3, 2, token)
        with self.assertRaises(RuleError):
            receive_donation(1, 1, 3, 2, token)
        after = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=3")
        movement = fetch_one(
            "SELECT quantity_change FROM stock_movements WHERE donation_id=%s", (donation_id,)
        )
        self.assertEqual(after["quantity_on_hand"], before["quantity_on_hand"] + 2)
        self.assertEqual(movement["quantity_change"], 2)

    def test_distribution_rejects_duplicate_and_excess(self):
        volunteer_id = add_volunteer("Test volunteer " + uuid4().hex[:8])
        assignment_id = assign_volunteer(
            volunteer_id, 1, datetime.now() - timedelta(hours=1), datetime.now() + timedelta(hours=1)
        )
        before = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=1")
        token = str(uuid4())
        distribution_id = distribute(1, 1, assignment_id, 3, token)
        with self.assertRaisesRegex(RuleError, "already processed"):
            distribute(1, 1, assignment_id, 3, token)
        with self.assertRaisesRegex(RuleError, "remaining assessed need"):
            distribute(1, 1, assignment_id, 3, str(uuid4()))
        with self.assertRaisesRegex(RuleError, "Not enough stock"):
            distribute(1, 1, assignment_id, 100, str(uuid4()))
        with self.assertRaisesRegex(RuleError, "family's camp"):
            distribute(4, 1, assignment_id, 1, str(uuid4()))
        after = fetch_one("SELECT quantity_on_hand FROM stock WHERE warehouse_id=1 AND item_id=1")
        movement = fetch_one(
            "SELECT quantity_change FROM stock_movements WHERE distribution_id=%s",
            (distribution_id,),
        )
        self.assertEqual(after["quantity_on_hand"], before["quantity_on_hand"] - 3)
        self.assertEqual(movement["quantity_change"], -3)
        self.assertEqual(
            fetch_one("SELECT remaining_quantity FROM v_unmet_needs WHERE need_id=1")["remaining_quantity"],
            2,
        )

    def test_stock_matches_movement_ledger(self):
        mismatches = fetch_one(
            "SELECT COUNT(*) AS mismatches FROM ("
            "SELECT s.warehouse_id, s.item_id FROM stock s "
            "LEFT JOIN stock_movements m ON m.warehouse_id=s.warehouse_id AND m.item_id=s.item_id "
            "GROUP BY s.warehouse_id, s.item_id, s.quantity_on_hand "
            "HAVING s.quantity_on_hand <> COALESCE(SUM(m.quantity_change), 0)"
            ") x"
        )
        self.assertEqual(mismatches["mismatches"], 0)

    def test_overlapping_volunteer_assignment_is_rejected(self):
        volunteer_id = add_volunteer("Overlap test " + uuid4().hex[:8])
        start = datetime.now() + timedelta(days=2)
        assign_volunteer(volunteer_id, 1, start, start + timedelta(hours=4))
        with self.assertRaisesRegex(RuleError, "overlapping"):
            assign_volunteer(
                volunteer_id,
                2,
                start + timedelta(hours=1),
                start + timedelta(hours=3),
            )

    def test_web_pages_and_catalogue_crud(self):
        client = app.test_client()
        for path in ("/", "/families", "/needs", "/donations", "/assignments", "/distributions", "/referrals", "/items", "/reports"):
            self.assertEqual(client.get(path).status_code, 200, path)
        with client.session_transaction() as session:
            csrf = session["csrf_token"]
        self.assertEqual(client.post("/items", data={"name": "Rejected"}).status_code, 400)
        item_name = "Test soap " + uuid4().hex[:8]
        response = client.post(
            "/items",
            data={"csrf_token": csrf, "name": item_name, "unit": "piece", "category": "Hygiene"},
            follow_redirects=True,
        )
        self.assertIn(b"Item added", response.data)
        item_id = fetch_one("SELECT item_id FROM relief_items WHERE name=%s", (item_name,))["item_id"]
        response = client.post(
            f"/items/{item_id}/edit",
            data={"csrf_token": csrf, "name": item_name + " updated", "unit": "piece", "category": "Hygiene"},
            follow_redirects=True,
        )
        self.assertIn(b"Item updated", response.data)
        response = client.post(
            f"/items/{item_id}/delete",
            data={"csrf_token": csrf},
            follow_redirects=True,
        )
        self.assertIn(b"Item deleted", response.data)
        self.assertIsNone(fetch_one("SELECT item_id FROM relief_items WHERE item_id=%s", (item_id,)))

    def test_web_family_registration_and_assessment(self):
        client = app.test_client()
        client.get("/families")
        with client.session_transaction() as session:
            csrf = session["csrf_token"]
        code = "F-TEST-" + uuid4().hex[:8]
        response = client.post(
            "/families",
            data={
                "csrf_token": csrf,
                "camp_id": "1",
                "registration_code": code,
                "member_name": ["Test Head", "Test Child"],
                "member_age": ["30", "7"],
                "member_relationship": ["Head", "Child"],
            },
            follow_redirects=True,
        )
        self.assertIn(b"Family registered", response.data)
        family_id = fetch_one("SELECT family_id FROM families WHERE registration_code=%s", (code,))["family_id"]
        response = client.post(
            f"/families/{family_id}/members",
            data={
                "csrf_token": csrf,
                "full_name": "Test Member",
                "age_at_registration": "20",
                "relationship_to_head": "Member",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Family member added", response.data)
        self.assertEqual(
            fetch_one("SELECT COUNT(*) AS count FROM persons WHERE family_id=%s", (family_id,))["count"],
            3,
        )
        response = client.post(
            "/needs",
            data={
                "csrf_token": csrf,
                "family_id": str(family_id),
                "item_id": "1",
                "relief_round": "TEST-ROUND",
                "quantity": "2",
                "urgency": "HIGH",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Need assessed", response.data)


if __name__ == "__main__":
    unittest.main()
