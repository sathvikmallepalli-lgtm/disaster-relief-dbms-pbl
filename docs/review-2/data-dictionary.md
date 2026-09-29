# Concise Data Dictionary

The authoritative types and constraints are in [`database/schema.sql`](../../database/schema.sql). This dictionary explains the fields that matter most to a reviewer.

| Table | Purpose | Main fields and meaning |
| --- | --- | --- |
| `disasters` | Relief event | `disaster_id` PK; `name`, `disaster_type`, `started_on`, `status` |
| `locations` | Reusable geographical description | `location_id` PK; `district`, `area`, `state` |
| `camps` | Temporary shelter | `camp_id` PK; `disaster_id`, `location_id` FKs; `name`, `capacity`, `opened_on` |
| `families` | Household registered at a camp | `family_id` PK; `camp_id` FK; unique `registration_code`; `registered_at`, `status` |
| `persons` | Member of a family | `person_id` PK; `family_id` FK; `full_name`, optional `age_at_registration`, `relationship_to_head` |
| `relief_items` | Supply catalogue | `item_id` PK; unique `name`; `unit`, `category` |
| `needs` | Assessed entitlement | `need_id` PK; `family_id`, `item_id` FKs; `relief_round`, `quantity_required`, `urgency`, `assessed_at` |
| `donors` | Source of supplies | `donor_id` PK; `name`, optional `contact` |
| `warehouses` | Stock storage point | `warehouse_id` PK; `location_id` FK; unique `name` |
| `donations` | One item receipt | `donation_id` PK; donor, warehouse, item FKs; `quantity_received`, `received_at`, unique `receipt_token` |
| `stock` | Current item balance in a warehouse | Composite PK/FKs `(warehouse_id, item_id)`; nonnegative `quantity_on_hand` |
| `volunteers` | Relief worker | `volunteer_id` PK; `full_name`, optional `phone` |
| `assignments` | Volunteer time at one camp | `assignment_id` PK; volunteer and camp FKs; `starts_at`, `ends_at` |
| `distributions` | Item quantity issued against a need | `distribution_id` PK; `need_id`, `warehouse_id`, `assignment_id` FKs; `quantity_issued`, `issued_at`, unique `request_token`; item comes from the need |
| `stock_movements` | Audit entry for receipt or issue | `movement_id` PK; stock FK; signed `quantity_change`; one unique donation or distribution source; `moved_at` |
| `referrals` | Follow-up for one person | `referral_id` PK; `person_id` FK; `destination`, `reason`, `referred_at`, `status` |

## Key terms

- **Relief round:** a short code such as `2026-W01` for one assessment period. A family can have one need per item in that round.
- **Request token:** a caller-generated identifier kept stable when retrying a distribution. A unique key prevents the same submission from being applied twice.
- **Receipt token:** the equivalent identifier for a donation receipt.
- **Remaining quantity:** `needs.quantity_required` minus the sum of `distributions.quantity_issued` for that need. It is calculated in `v_unmet_needs` rather than stored.
- **Stock movement:** positive quantity for a donation receipt, negative quantity for a distribution issue. Its source reference connects the ledger entry to the event.
