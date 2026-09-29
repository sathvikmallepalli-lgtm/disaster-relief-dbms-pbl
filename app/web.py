"""Local-only Flask interface for the disaster relief database."""

import os
import secrets
from datetime import datetime
from itertools import zip_longest
from uuid import uuid4

import mysql.connector
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from app.db import fetch_all, fetch_one
from app.services import (
    RuleError,
    add_donor,
    add_family_member,
    add_volunteer,
    assess_need,
    assign_volunteer,
    create_item,
    create_referral,
    delete_item,
    distribute,
    receive_donation,
    register_family,
    update_item,
    update_referral_status,
)


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


@app.before_request
def protect_forms():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)
    if request.method == "POST" and request.form.get("csrf_token") != session["csrf_token"]:
        abort(400, "Invalid form token. Reload the page and try again.")


@app.context_processor
def template_values():
    return {"csrf_token": session.get("csrf_token", ""), "today": datetime.now()}


def save_action(action, success_message, destination):
    try:
        action()
        flash(success_message, "success")
    except RuleError as exc:
        flash(str(exc), "error")
    except ValueError:
        flash("Check the date, time, and number fields.", "error")
    except mysql.connector.Error:
        app.logger.exception("Database operation failed")
        flash("Database operation failed. Check the local database connection and input.", "error")
    return redirect(url_for(destination))


@app.get("/")
def dashboard():
    counts = fetch_one(
        "SELECT "
        "(SELECT COUNT(*) FROM camps) AS camps, "
        "(SELECT COUNT(*) FROM families WHERE status='ACTIVE') AS families, "
        "(SELECT COUNT(*) FROM persons) AS people, "
        "(SELECT COUNT(*) FROM v_unmet_needs) AS unmet"
    )
    queue = fetch_all(
        "SELECT registration_code, camp_name, item_name, urgency, remaining_quantity, assessed_at "
        "FROM v_unmet_needs "
        "ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id LIMIT 6"
    )
    return render_template("dashboard.html", counts=counts, queue=queue)


@app.route("/families", methods=["GET", "POST"])
def families():
    if request.method == "POST":
        names = request.form.getlist("member_name")
        ages = request.form.getlist("member_age")
        relationships = request.form.getlist("member_relationship")
        members = [
            {"full_name": name, "age_at_registration": age, "relationship_to_head": relationship}
            for name, age, relationship in zip_longest(names, ages, relationships, fillvalue="")
        ]
        return save_action(
            lambda: register_family(
                request.form.get("camp_id"), request.form.get("registration_code", ""), members
            ),
            "Family registered.",
            "families",
        )
    search = request.args.get("q", "").strip()
    rows = fetch_all(
        "SELECT f.family_id, f.registration_code, f.registered_at, f.status, c.name AS camp_name, "
        "COALESCE(p.member_count, 0) AS member_count "
        "FROM families f JOIN camps c ON c.camp_id=f.camp_id "
        "LEFT JOIN (SELECT family_id, COUNT(*) AS member_count FROM persons GROUP BY family_id) p "
        "ON p.family_id=f.family_id "
        "WHERE f.registration_code LIKE %s ORDER BY f.family_id DESC",
        (f"%{search}%",),
    )
    camps = fetch_all("SELECT camp_id, name FROM camps ORDER BY name")
    return render_template("families.html", rows=rows, camps=camps, search=search)


@app.get("/families/<int:family_id>")
def family_detail(family_id):
    family = fetch_one(
        "SELECT f.*, c.name AS camp_name FROM families f "
        "JOIN camps c ON c.camp_id=f.camp_id WHERE f.family_id=%s",
        (family_id,),
    )
    if not family:
        abort(404)
    members = fetch_all("SELECT * FROM persons WHERE family_id=%s ORDER BY person_id", (family_id,))
    needs = fetch_all(
        "SELECT n.need_id, i.name AS item_name, n.relief_round, n.urgency, "
        "n.quantity_required, COALESCE(SUM(d.quantity_issued), 0) AS quantity_issued "
        "FROM needs n JOIN relief_items i ON i.item_id=n.item_id "
        "LEFT JOIN distributions d ON d.need_id=n.need_id "
        "WHERE n.family_id=%s "
        "GROUP BY n.need_id, i.name, n.relief_round, n.urgency, n.quantity_required "
        "ORDER BY n.assessed_at DESC",
        (family_id,),
    )
    return render_template("family_detail.html", family=family, members=members, needs=needs)


@app.post("/families/<int:family_id>/members")
def family_member_add(family_id):
    try:
        add_family_member(
            family_id,
            request.form.get("full_name", ""),
            request.form.get("age_at_registration", ""),
            request.form.get("relationship_to_head", ""),
        )
        flash("Family member added.", "success")
    except RuleError as exc:
        flash(str(exc), "error")
    except mysql.connector.Error:
        app.logger.exception("Family member creation failed")
        flash("Could not add the member. Check the database connection.", "error")
    return redirect(url_for("family_detail", family_id=family_id))


@app.route("/needs", methods=["GET", "POST"])
def needs():
    if request.method == "POST":
        return save_action(
            lambda: assess_need(
                request.form.get("family_id"),
                request.form.get("item_id"),
                request.form.get("relief_round", ""),
                request.form.get("quantity"),
                request.form.get("urgency", ""),
            ),
            "Need assessed.",
            "needs",
        )
    rows = fetch_all(
        "SELECT * FROM v_unmet_needs "
        "ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id"
    )
    families_list = fetch_all(
        "SELECT family_id, registration_code FROM families WHERE status='ACTIVE' ORDER BY registration_code"
    )
    items = fetch_all("SELECT item_id, name, unit FROM relief_items ORDER BY name")
    return render_template("needs.html", rows=rows, families=families_list, items=items)


@app.route("/donations", methods=["GET", "POST"])
def donations():
    if request.method == "POST":
        return save_action(
            lambda: receive_donation(
                request.form.get("donor_id"),
                request.form.get("warehouse_id"),
                request.form.get("item_id"),
                request.form.get("quantity"),
                request.form.get("receipt_token"),
            ),
            "Donation received and stock updated.",
            "donations",
        )
    rows = fetch_all(
        "SELECT d.donation_id, d.received_at, r.name AS donor_name, w.name AS warehouse_name, "
        "i.name AS item_name, d.quantity_received "
        "FROM donations d JOIN donors r ON r.donor_id=d.donor_id "
        "JOIN warehouses w ON w.warehouse_id=d.warehouse_id "
        "JOIN relief_items i ON i.item_id=d.item_id ORDER BY d.received_at DESC, d.donation_id DESC"
    )
    return render_template(
        "donations.html",
        rows=rows,
        donors=fetch_all("SELECT donor_id, name FROM donors ORDER BY name"),
        warehouses=fetch_all("SELECT warehouse_id, name FROM warehouses ORDER BY name"),
        items=fetch_all("SELECT item_id, name, unit FROM relief_items ORDER BY name"),
        token=str(uuid4()),
    )


@app.post("/donors")
def donors_add():
    return save_action(
        lambda: add_donor(request.form.get("name", ""), request.form.get("contact", "")),
        "Donor added.",
        "donations",
    )


@app.route("/assignments", methods=["GET", "POST"])
def assignments():
    if request.method == "POST":
        def action():
            assign_volunteer(
                request.form.get("volunteer_id"),
                request.form.get("camp_id"),
                datetime.fromisoformat(request.form.get("starts_at", "")),
                datetime.fromisoformat(request.form.get("ends_at", "")),
            )
        return save_action(action, "Volunteer assigned.", "assignments")
    rows = fetch_all(
        "SELECT a.assignment_id, v.full_name AS volunteer_name, c.name AS camp_name, "
        "a.starts_at, a.ends_at FROM assignments a "
        "JOIN volunteers v ON v.volunteer_id=a.volunteer_id "
        "JOIN camps c ON c.camp_id=a.camp_id ORDER BY a.starts_at DESC"
    )
    return render_template(
        "assignments.html",
        rows=rows,
        volunteers=fetch_all("SELECT volunteer_id, full_name FROM volunteers ORDER BY full_name"),
        camps=fetch_all("SELECT camp_id, name FROM camps ORDER BY name"),
    )


@app.post("/volunteers")
def volunteers_add():
    return save_action(
        lambda: add_volunteer(request.form.get("full_name", ""), request.form.get("phone", "")),
        "Volunteer added.",
        "assignments",
    )


@app.route("/distributions", methods=["GET", "POST"])
def distributions():
    if request.method == "POST":
        return save_action(
            lambda: distribute(
                request.form.get("need_id"),
                request.form.get("warehouse_id"),
                request.form.get("assignment_id"),
                request.form.get("quantity"),
                request.form.get("request_token"),
            ),
            "Distribution recorded and stock reduced.",
            "distributions",
        )
    return render_template(
        "distributions.html",
        rows=fetch_all(
            "SELECT issued_at, registration_code, camp_name, item_name, quantity_issued, "
            "warehouse_name, volunteer_name FROM v_distribution_history "
            "ORDER BY issued_at DESC, distribution_id DESC"
        ),
        needs=fetch_all(
            "SELECT * FROM v_unmet_needs "
            "ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id"
        ),
        warehouses=fetch_all("SELECT warehouse_id, name FROM warehouses ORDER BY name"),
        assignments=fetch_all(
            "SELECT a.assignment_id, v.full_name, c.name AS camp_name "
            "FROM assignments a JOIN volunteers v ON v.volunteer_id=a.volunteer_id "
            "JOIN camps c ON c.camp_id=a.camp_id "
            "WHERE a.starts_at <= NOW() AND a.ends_at > NOW() ORDER BY c.name, v.full_name"
        ),
        token=str(uuid4()),
    )


@app.route("/referrals", methods=["GET", "POST"])
def referrals():
    if request.method == "POST":
        return save_action(
            lambda: create_referral(
                request.form.get("person_id"),
                request.form.get("destination", ""),
                request.form.get("reason", ""),
            ),
            "Referral recorded.",
            "referrals",
        )
    rows = fetch_all(
        "SELECT r.referral_id, p.full_name AS person_name, f.registration_code, "
        "r.destination, r.reason, r.referred_at, r.status "
        "FROM referrals r JOIN persons p ON p.person_id=r.person_id "
        "JOIN families f ON f.family_id=p.family_id "
        "ORDER BY r.referred_at DESC, r.referral_id DESC"
    )
    persons = fetch_all(
        "SELECT p.person_id, p.full_name, f.registration_code FROM persons p "
        "JOIN families f ON f.family_id=p.family_id ORDER BY f.registration_code, p.full_name"
    )
    return render_template("referrals.html", rows=rows, persons=persons)


@app.post("/referrals/<int:referral_id>/status")
def referrals_status(referral_id):
    return save_action(
        lambda: update_referral_status(referral_id, request.form.get("status", "")),
        "Referral status updated.",
        "referrals",
    )


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        return save_action(
            lambda: create_item(
                request.form.get("name", ""),
                request.form.get("unit", ""),
                request.form.get("category", ""),
            ),
            "Item added.",
            "items",
        )
    return render_template("items.html", rows=fetch_all("SELECT * FROM relief_items ORDER BY name"))


@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
def items_edit(item_id):
    if request.method == "POST":
        return save_action(
            lambda: update_item(
                item_id,
                request.form.get("name", ""),
                request.form.get("unit", ""),
                request.form.get("category", ""),
            ),
            "Item updated.",
            "items",
        )
    item = fetch_one("SELECT * FROM relief_items WHERE item_id=%s", (item_id,))
    if not item:
        abort(404)
    return render_template("item_edit.html", item=item)


@app.post("/items/<int:item_id>/delete")
def items_delete(item_id):
    return save_action(lambda: delete_item(item_id), "Item deleted.", "items")


@app.get("/reports")
def reports():
    sections = [
        ("Camp population", fetch_all(
            "SELECT camp_name, disaster_name, family_count, person_count "
            "FROM v_camp_population ORDER BY camp_name"
        )),
        ("Unmet needs", fetch_all(
            "SELECT registration_code, camp_name, item_name, urgency, "
            "quantity_required, quantity_issued, remaining_quantity FROM v_unmet_needs "
            "ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id"
        )),
        ("Warehouse stock", fetch_all(
            "SELECT warehouse_name, item_name, unit, quantity_on_hand "
            "FROM v_stock ORDER BY warehouse_name, item_name"
        )),
        ("Distributions", fetch_all(
            "SELECT issued_at, registration_code, camp_name, item_name, quantity_issued, "
            "volunteer_name FROM v_distribution_history ORDER BY issued_at DESC"
        )),
        ("Donor contributions", fetch_all(
            "SELECT donor_name, item_name, unit, quantity_donated "
            "FROM v_donor_contributions ORDER BY donor_name, item_name"
        )),
        ("Volunteer work", fetch_all(
            "SELECT volunteer_name, camp_name, starts_at, ends_at, distributions_handled "
            "FROM v_volunteer_work ORDER BY volunteer_name, starts_at"
        )),
        ("Open referrals", fetch_all(
            "SELECT person_name, registration_code, camp_name, destination, reason "
            "FROM v_open_referrals ORDER BY referred_at"
        )),
    ]
    return render_template("reports.html", sections=sections)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("APP_PORT", "5000")), debug=False)
