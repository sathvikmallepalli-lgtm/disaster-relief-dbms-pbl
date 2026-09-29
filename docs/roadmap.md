# Review Roadmap

This repository will keep the evidence for all three reviews in one place. A review is complete only when its files match a working demonstration.

| Review | Required evidence | Planned repository evidence | Demonstration |
| --- | --- | --- | --- |
| 1 · Week 7 | Problem, scope, objectives, users, functional requirements, conceptual ERD, initial relational schema | `docs/review-1/` and root `README.md` | Explain one family's path from registration to distribution using the ERD |
| 2 · Week 11 | Functional dependencies and 3NF, data dictionary, DDL with constraints, sample data, joins, subqueries, aggregation, views, prototype | `docs/review-2/`, `database/` | Create sample records and run stock, unmet-needs, camp, donor, volunteer, distribution, and referral queries |
| 3 · Week 16 | Connected Python app, CRUD, search, validation, reports, error handling, source, scripts, test data, output screens, report, viva | `app/`, `tests/`, `docs/review-3/` | Register family; assess need; receive stock; assign volunteer; distribute; show reports and rejected invalid operations |

## Practical innovation

The unmet-needs queue combines **urgency**, **time waiting**, and **remaining quantity** from recorded assessments and distributions. The order is visible and explainable. Staff still make the final allocation decision. A stock movement log makes each receipt or issue auditable.

## Important database rules to demonstrate

- A family has at most one assessment for the same item and relief round.
- Repeating the same distribution request must not issue stock twice.
- Total issued for a need cannot exceed its assessed quantity.
- A distribution cannot take stock below zero.
- A volunteer cannot have overlapping assignments.
- Every stock change has a corresponding movement record.

Unique keys and row-level checks handle simple rules. Rules involving totals or time overlaps need transaction-safe database logic, which will be designed and demonstrated in Review 2.
