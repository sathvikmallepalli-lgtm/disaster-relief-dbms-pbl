# Normalization to Third Normal Form

## Starting point

A single paper register might put camp details, every family member, requested items, donor names, stock totals, and issue dates in one row. One family can have many members and many needs, while an item can receive many donations and distributions. That design repeats data and makes updates unreliable.

## Functional dependencies

Each table has a key that determines its non-key fields. The most important dependencies are:

| Relation | Key → dependent attributes |
| --- | --- |
| `disasters` | `disaster_id → name, disaster_type, started_on, status` |
| `locations` | `location_id → district, area, state` |
| `camps` | `camp_id → disaster_id, location_id, name, capacity, opened_on` |
| `families` | `family_id → camp_id, registration_code, registered_at, status` |
| `persons` | `person_id → family_id, full_name, age_at_registration, relationship_to_head` |
| `relief_items` | `item_id → name, unit, category` |
| `needs` | `need_id → family_id, item_id, relief_round, quantity_required, urgency, assessed_at`; also `(family_id, item_id, relief_round)` uniquely identifies an assessment |
| `donors` | `donor_id → name, contact` |
| `warehouses` | `warehouse_id → location_id, name` |
| `donations` | `donation_id → donor_id, warehouse_id, item_id, quantity_received, received_at, receipt_token` |
| `stock` | `(warehouse_id, item_id) → quantity_on_hand` |
| `volunteers` | `volunteer_id → full_name, phone` |
| `assignments` | `assignment_id → volunteer_id, camp_id, starts_at, ends_at` |
| `distributions` | `distribution_id → need_id, warehouse_id, assignment_id, request_token, quantity_issued, issued_at` |
| `stock_movements` | `movement_id → warehouse_id, item_id, movement_type, quantity_change, donation_id, distribution_id, moved_at` |
| `referrals` | `referral_id → person_id, destination, reason, referred_at, status` |

## 1NF, 2NF, and 3NF checks

**First Normal Form:** Each field holds one value. Members, item needs, donations, distributions, and assignments have separate rows rather than comma-separated lists. Each table has a primary key.

**Second Normal Form:** The only composite-key table is `stock`. Its balance depends on the whole `(warehouse_id, item_id)` pair. Other tables use a single-column primary key, so they have no partial dependency on a key subset.

**Third Normal Form:** Descriptive information stays with the entity it describes. A distribution stores the needed IDs and quantity, while item name and unit come from `relief_items`, family registration code comes from `families`, and volunteer name comes from `volunteers`. Camp location information stays in `locations`. Reports join these tables when they need the descriptions.

The Review 1 draft included `distributions.item_id`. Normalization showed that `need_id` already determines the item, so the implementation removes that repeated column. The distribution transaction reads the item's ID from `needs` and locks the matching warehouse stock row.

`stock.quantity_on_hand` is a maintained operational balance, and `stock_movements` is an append-only audit log. They repeat information that can be derived from donation and distribution events. This is a deliberate, limited exception for fast balance checks and traceability: every receipt or issue updates all affected records in one transaction, and the reconciliation query in `database/reports.sql` checks that balance and movement total agree. The remaining entity tables avoid the main insertion, update, and deletion anomalies of the original combined register.
