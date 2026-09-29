# Initial Relational Schema

This is the Review 1 mapping from the conceptual ERD. `PK` means primary key; `FK` means foreign key; `UK` means unique key. Complete data types, default values, indexes, and implementation SQL will be part of Review 2.

| Table | Primary key | Foreign keys | Other important fields and proposed rules |
| --- | --- | --- | --- |
| `disasters` | `disaster_id` | — | `name`, `disaster_type`, `started_on`, `status` |
| `locations` | `location_id` | — | `district`, `area`, `state` |
| `camps` | `camp_id` | `disaster_id → disasters`, `location_id → locations` | `name`, `capacity`, `opened_on` |
| `families` | `family_id` | `camp_id → camps` | `registration_code` UK, `registered_at`, `status` |
| `persons` | `person_id` | `family_id → families` | `full_name`, `age_at_registration`, `relationship_to_head` |
| `relief_items` | `item_id` | — | `name` UK, `unit`, `category` |
| `needs` | `need_id` | `family_id → families`, `item_id → relief_items` | `relief_round`, `quantity_required`, `urgency`, `assessed_at`; UK (`family_id`, `item_id`, `relief_round`) |
| `donors` | `donor_id` | — | `name`, `contact` (optional) |
| `warehouses` | `warehouse_id` | `location_id → locations` | `name` |
| `donations` | `donation_id` | `donor_id → donors`, `warehouse_id → warehouses`, `item_id → relief_items` | `quantity_received`, `received_at` |
| `stock` | (`warehouse_id`, `item_id`) | `warehouse_id → warehouses`, `item_id → relief_items` | `quantity_on_hand ≥ 0` |
| `stock_movements` | `movement_id` | (`warehouse_id`, `item_id`) → `stock` | `movement_type`, `quantity_change`, `donation_id` or `distribution_id`, `moved_at` |
| `volunteers` | `volunteer_id` | — | `full_name`, `phone` (optional) |
| `assignments` | `assignment_id` | `volunteer_id → volunteers`, `camp_id → camps` | `starts_at`, `ends_at`; no overlap for one volunteer |
| `distributions` | `distribution_id` | `need_id → needs`, `assignment_id → assignments`, (`warehouse_id`, `item_id`) → `stock` | `request_token` UK, `quantity_issued`, `issued_at`; item must match the need |
| `referrals` | `referral_id` | `person_id → persons` | `destination`, `reason`, `referred_at`, `status` |

## Relationship and design notes

- `families.camp_id` identifies the family's current camp. Historical camp transfers are outside the first MVP. If the scope later requires transfers, add a transfer history table instead of overwriting history silently.
- `needs.relief_round` is a simple label such as `2026-W01`. The unique key avoids duplicate assessment of one item for a family in a round. Multiple distribution events may fulfill that one need, provided their total stays within `quantity_required`.
- `distributions.item_id` is included to reference a specific stock row. It must equal the item's ID on the related need. Review 2 will enforce this in a transaction or with a composite relationship.
- `stock_movements` is an append-only log. A receipt points to a donation; an issue points to a distribution. Exactly one of those source references is set for each movement, and each source is posted once. This lets the balance be checked against the history.
- Rules about sums, stock availability, and time interval overlap involve multiple rows; a simple `CHECK` constraint alone cannot enforce them. Review 2 will specify the transaction logic and tests.

## Planned report questions

1. How many people are registered in each camp?
2. Which needs are still unmet, ordered by urgency and assessment time?
3. How much of each item is available at each warehouse?
4. What was distributed to each family, when, and by whom?
5. Which donors contributed each item?
6. What assignments and distributions did each volunteer handle?
7. Which referrals remain open?
