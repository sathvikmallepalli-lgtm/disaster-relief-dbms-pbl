"""Small command-line prototype for Review 2 demonstrations."""

import argparse
from datetime import datetime

from app.db import fetch_all
from app.services import RuleError, assign_volunteer, distribute, receive_donation


REPORTS = {
    "camps": "SELECT * FROM v_camp_population ORDER BY camp_name",
    "unmet": (
        "SELECT * FROM v_unmet_needs "
        "ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id"
    ),
    "stock": "SELECT * FROM v_stock ORDER BY warehouse_name, item_name",
    "distributions": "SELECT * FROM v_distribution_history ORDER BY issued_at DESC",
    "donors": "SELECT * FROM v_donor_contributions ORDER BY donor_name, item_name",
    "volunteers": "SELECT * FROM v_volunteer_work ORDER BY volunteer_name, starts_at",
    "referrals": "SELECT * FROM v_open_referrals ORDER BY referred_at",
    "ledger": (
        "SELECT s.warehouse_id, s.item_id, s.quantity_on_hand, "
        "COALESCE(SUM(m.quantity_change), 0) AS movement_total "
        "FROM stock s LEFT JOIN stock_movements m "
        "ON m.warehouse_id=s.warehouse_id AND m.item_id=s.item_id "
        "GROUP BY s.warehouse_id, s.item_id, s.quantity_on_hand "
        "ORDER BY s.warehouse_id, s.item_id"
    ),
}


def print_rows(rows):
    if not rows:
        print("No records found.")
        return
    columns = list(rows[0])
    widths = {
        column: max(len(column), *(len(str(row[column])) for row in rows))
        for column in columns
    }
    print(" | ".join(column.ljust(widths[column]) for column in columns))
    print("-+-".join("-" * widths[column] for column in columns))
    for row in rows:
        print(" | ".join(str(row[column]).ljust(widths[column]) for column in columns))


def main():
    parser = argparse.ArgumentParser(description="Disaster relief MySQL prototype")
    commands = parser.add_subparsers(dest="command", required=True)

    report = commands.add_parser("report", help="Show a database report")
    report.add_argument("name", choices=REPORTS)

    receipt = commands.add_parser("receive", help="Receive a donated item")
    receipt.add_argument("--donor", type=int, required=True)
    receipt.add_argument("--warehouse", type=int, required=True)
    receipt.add_argument("--item", type=int, required=True)
    receipt.add_argument("--quantity", type=int, required=True)
    receipt.add_argument("--token", help="Optional stable request token for retry checks")

    assignment = commands.add_parser("assign", help="Assign a volunteer")
    assignment.add_argument("--volunteer", type=int, required=True)
    assignment.add_argument("--camp", type=int, required=True)
    assignment.add_argument("--start", required=True, help="YYYY-MM-DDTHH:MM")
    assignment.add_argument("--end", required=True, help="YYYY-MM-DDTHH:MM")

    issue = commands.add_parser("distribute", help="Issue stock against a need")
    issue.add_argument("--need", type=int, required=True)
    issue.add_argument("--warehouse", type=int, required=True)
    issue.add_argument("--assignment", type=int, required=True)
    issue.add_argument("--quantity", type=int, required=True)
    issue.add_argument("--token", help="Optional stable request token for retry checks")

    args = parser.parse_args()
    try:
        if args.command == "report":
            print_rows(fetch_all(REPORTS[args.name]))
        elif args.command == "receive":
            result = receive_donation(args.donor, args.warehouse, args.item, args.quantity, args.token)
            print(f"Donation receipt #{result} recorded.")
        elif args.command == "assign":
            result = assign_volunteer(
                args.volunteer,
                args.camp,
                datetime.fromisoformat(args.start),
                datetime.fromisoformat(args.end),
            )
            print(f"Volunteer assignment #{result} recorded.")
        elif args.command == "distribute":
            result = distribute(args.need, args.warehouse, args.assignment, args.quantity, args.token)
            print(f"Distribution #{result} recorded.")
    except RuleError as exc:
        parser.exit(2, f"Rejected: {exc}\n")


if __name__ == "__main__":
    main()
