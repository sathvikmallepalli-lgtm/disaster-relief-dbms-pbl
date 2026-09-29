"""Business rules for registration, receipts, scheduling, and distribution.

Cross-row rules use MySQL row locks inside transactions. Forms and the command-line
prototype call the same functions, so both demonstrate the same database behavior.
"""

from datetime import datetime
from uuid import uuid4

import mysql.connector

from app.db import get_connection


class RuleError(ValueError):
    """The requested operation violates a project business rule."""


def _positive_quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError) as exc:
        raise RuleError("Quantity must be a whole number.") from exc
    if quantity <= 0:
        raise RuleError("Quantity must be greater than zero.")
    return quantity


def _run_transaction(operation, duplicate_message="A record with these details already exists."):
    connection = get_connection()
    try:
        # READ COMMITTED makes the post-lock total query see transactions that
        # committed while this operation was waiting for the need row.
        connection.start_transaction(isolation_level="READ COMMITTED")
        result = operation(connection)
        connection.commit()
        return result
    except mysql.connector.IntegrityError as exc:
        connection.rollback()
        raise RuleError(duplicate_message) from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def register_family(camp_id, registration_code, members):
    code = registration_code.strip()
    if not code:
        raise RuleError("Registration code is required.")
    cleaned = []
    for member in members:
        name = member["full_name"].strip()
        if not name:
            continue
        age = member.get("age_at_registration")
        if age in ("", None):
            age = None
        else:
            try:
                age = int(age)
            except ValueError as exc:
                raise RuleError("Age must be a whole number.") from exc
            if age < 0 or age > 120:
                raise RuleError("Age must be between 0 and 120.")
        cleaned.append((name, age, member.get("relationship_to_head", "Member").strip() or "Member"))
    if not cleaned:
        raise RuleError("Add at least one family member.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO families (camp_id, registration_code) VALUES (%s, %s)",
            (camp_id, code),
        )
        family_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO persons (family_id, full_name, age_at_registration, relationship_to_head) "
            "VALUES (%s, %s, %s, %s)",
            [(family_id, name, age, relationship) for name, age, relationship in cleaned],
        )
        return family_id

    return _run_transaction(operation, "That family registration code is already used, or the camp is invalid.")


def add_family_member(family_id, full_name, age_at_registration, relationship_to_head):
    full_name = full_name.strip()
    relationship_to_head = relationship_to_head.strip() or "Member"
    if not full_name:
        raise RuleError("Member name is required.")
    if age_at_registration in ("", None):
        age = None
    else:
        try:
            age = int(age_at_registration)
        except ValueError as exc:
            raise RuleError("Age must be a whole number.") from exc
        if not 0 <= age <= 120:
            raise RuleError("Age must be between 0 and 120.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO persons (family_id, full_name, age_at_registration, relationship_to_head) "
            "VALUES (%s, %s, %s, %s)",
            (family_id, full_name, age, relationship_to_head),
        )
        return cursor.lastrowid

    return _run_transaction(operation, "Family was not found.")


def assess_need(family_id, item_id, relief_round, quantity, urgency):
    quantity = _positive_quantity(quantity)
    relief_round = relief_round.strip()
    urgency = urgency.upper().strip()
    if not relief_round:
        raise RuleError("Relief round is required.")
    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        raise RuleError("Choose high, medium, or low urgency.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO needs (family_id, item_id, relief_round, quantity_required, urgency) "
            "VALUES (%s, %s, %s, %s, %s)",
            (family_id, item_id, relief_round, quantity, urgency),
        )
        return cursor.lastrowid

    return _run_transaction(operation, "This family already has an assessment for that item and relief round.")


def receive_donation(donor_id, warehouse_id, item_id, quantity, receipt_token=None):
    quantity = _positive_quantity(quantity)
    token = receipt_token or str(uuid4())

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO donations (donor_id, warehouse_id, item_id, quantity_received, receipt_token) "
            "VALUES (%s, %s, %s, %s, %s)",
            (donor_id, warehouse_id, item_id, quantity, token),
        )
        donation_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO stock (warehouse_id, item_id, quantity_on_hand) VALUES (%s, %s, 0) "
            "ON DUPLICATE KEY UPDATE quantity_on_hand = quantity_on_hand",
            (warehouse_id, item_id),
        )
        cursor.execute(
            "UPDATE stock SET quantity_on_hand = quantity_on_hand + %s "
            "WHERE warehouse_id = %s AND item_id = %s",
            (quantity, warehouse_id, item_id),
        )
        cursor.execute(
            "INSERT INTO stock_movements "
            "(warehouse_id, item_id, movement_type, quantity_change, donation_id) "
            "VALUES (%s, %s, 'RECEIPT', %s, %s)",
            (warehouse_id, item_id, quantity, donation_id),
        )
        return donation_id

    return _run_transaction(operation, "This donation receipt was already recorded, or a reference is invalid.")


def assign_volunteer(volunteer_id, camp_id, starts_at, ends_at):
    if not isinstance(starts_at, datetime) or not isinstance(ends_at, datetime):
        raise RuleError("Assignment dates and times are required.")
    if ends_at <= starts_at:
        raise RuleError("Assignment end must be after its start.")

    def operation(connection):
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT volunteer_id FROM volunteers WHERE volunteer_id = %s FOR UPDATE",
            (volunteer_id,),
        )
        if cursor.fetchone() is None:
            raise RuleError("Volunteer does not exist.")
        cursor.execute(
            "SELECT assignment_id FROM assignments "
            "WHERE volunteer_id = %s AND starts_at < %s AND ends_at > %s LIMIT 1",
            (volunteer_id, ends_at, starts_at),
        )
        if cursor.fetchone():
            raise RuleError("Volunteer already has an overlapping assignment.")
        cursor.execute(
            "INSERT INTO assignments (volunteer_id, camp_id, starts_at, ends_at) "
            "VALUES (%s, %s, %s, %s)",
            (volunteer_id, camp_id, starts_at, ends_at),
        )
        return cursor.lastrowid

    return _run_transaction(operation, "The camp or volunteer is invalid.")


def distribute(need_id, warehouse_id, assignment_id, quantity, request_token=None):
    quantity = _positive_quantity(quantity)
    token = request_token or str(uuid4())

    def operation(connection):
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT distribution_id FROM distributions WHERE request_token = %s", (token,))
        if cursor.fetchone():
            raise RuleError("This distribution request was already processed.")
        cursor.execute(
            "SELECT n.item_id, n.quantity_required, f.camp_id "
            "FROM needs n JOIN families f ON f.family_id = n.family_id "
            "WHERE n.need_id = %s AND f.status = 'ACTIVE' FOR UPDATE",
            (need_id,),
        )
        need = cursor.fetchone()
        if not need:
            raise RuleError("Active need was not found.")
        cursor.execute(
            "SELECT quantity_on_hand FROM stock "
            "WHERE warehouse_id = %s AND item_id = %s FOR UPDATE",
            (warehouse_id, need["item_id"]),
        )
        stock = cursor.fetchone()
        if not stock or stock["quantity_on_hand"] < quantity:
            raise RuleError("Not enough stock is available.")
        cursor.execute(
            "SELECT camp_id, starts_at, ends_at FROM assignments WHERE assignment_id = %s",
            (assignment_id,),
        )
        assignment = cursor.fetchone()
        now = datetime.now()
        if not assignment or assignment["camp_id"] != need["camp_id"]:
            raise RuleError("Choose a volunteer assignment at this family's camp.")
        if not (assignment["starts_at"] <= now < assignment["ends_at"]):
            raise RuleError("The volunteer assignment is not active now.")
        cursor.execute(
            "SELECT COALESCE(SUM(quantity_issued), 0) AS issued "
            "FROM distributions WHERE need_id = %s",
            (need_id,),
        )
        issued = cursor.fetchone()["issued"]
        if issued + quantity > need["quantity_required"]:
            raise RuleError("Issue exceeds the family's remaining assessed need.")
        cursor.execute(
            "INSERT INTO distributions "
            "(need_id, warehouse_id, assignment_id, request_token, quantity_issued) "
            "VALUES (%s, %s, %s, %s, %s)",
            (need_id, warehouse_id, assignment_id, token, quantity),
        )
        distribution_id = cursor.lastrowid
        cursor.execute(
            "UPDATE stock SET quantity_on_hand = quantity_on_hand - %s "
            "WHERE warehouse_id = %s AND item_id = %s AND quantity_on_hand >= %s",
            (quantity, warehouse_id, need["item_id"], quantity),
        )
        if cursor.rowcount != 1:
            raise RuleError("Not enough stock is available.")
        cursor.execute(
            "INSERT INTO stock_movements "
            "(warehouse_id, item_id, movement_type, quantity_change, distribution_id) "
            "VALUES (%s, %s, 'ISSUE', %s, %s)",
            (warehouse_id, need["item_id"], -quantity, distribution_id),
        )
        return distribution_id

    return _run_transaction(operation, "This distribution request was already processed, or a reference is invalid.")


def create_referral(person_id, destination, reason):
    destination = destination.strip()
    reason = reason.strip()
    if not destination or not reason:
        raise RuleError("Referral destination and reason are required.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO referrals (person_id, destination, reason) VALUES (%s, %s, %s)",
            (person_id, destination, reason),
        )
        return cursor.lastrowid

    return _run_transaction(operation, "Person does not exist.")


def update_referral_status(referral_id, status):
    status = status.upper().strip()
    if status not in {"OPEN", "COMPLETED", "CANCELLED"}:
        raise RuleError("Choose open, completed, or cancelled.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute("UPDATE referrals SET status = %s WHERE referral_id = %s", (status, referral_id))
        if cursor.rowcount == 0:
            raise RuleError("Referral was not found or already has that status.")

    _run_transaction(operation)


def add_donor(name, contact=None):
    name = name.strip()
    if not name:
        raise RuleError("Donor name is required.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO donors (name, contact) VALUES (%s, %s)", (name, contact or None))
        return cursor.lastrowid

    return _run_transaction(operation)


def add_volunteer(full_name, phone=None):
    full_name = full_name.strip()
    if not full_name:
        raise RuleError("Volunteer name is required.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO volunteers (full_name, phone) VALUES (%s, %s)",
            (full_name, phone or None),
        )
        return cursor.lastrowid

    return _run_transaction(operation)


def create_item(name, unit, category):
    name, unit, category = name.strip(), unit.strip(), category.strip()
    if not name or not unit or not category:
        raise RuleError("Item name, unit, and category are required.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO relief_items (name, unit, category) VALUES (%s, %s, %s)",
            (name, unit, category),
        )
        return cursor.lastrowid

    return _run_transaction(operation, "An item with this name already exists.")


def update_item(item_id, name, unit, category):
    name, unit, category = name.strip(), unit.strip(), category.strip()
    if not name or not unit or not category:
        raise RuleError("Item name, unit, and category are required.")

    def operation(connection):
        cursor = connection.cursor()
        cursor.execute("SELECT item_id FROM relief_items WHERE item_id = %s", (item_id,))
        if not cursor.fetchone():
            raise RuleError("Item was not found.")
        cursor.execute(
            "UPDATE relief_items SET name=%s, unit=%s, category=%s WHERE item_id=%s",
            (name, unit, category, item_id),
        )

    _run_transaction(operation, "An item with this name already exists.")


def delete_item(item_id):
    def operation(connection):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM relief_items WHERE item_id = %s", (item_id,))
        if cursor.rowcount == 0:
            raise RuleError("Item was not found.")

    _run_transaction(operation, "This item is already used by a need, donation, or stock record.")
