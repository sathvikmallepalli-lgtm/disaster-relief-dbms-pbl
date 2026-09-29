# Conceptual ER Diagram

The diagram includes every principal entity named in Project 60. `DONORS` and `STOCK_MOVEMENTS` are added to support donor reporting and traceable receipts/issues. A relief round is stored as a code on each need so the same family can be assessed again later.

```mermaid
erDiagram
    DISASTERS ||--o{ CAMPS : has
    LOCATIONS ||--o{ CAMPS : hosts
    LOCATIONS ||--o{ WAREHOUSES : hosts
    CAMPS ||--o{ FAMILIES : registers
    FAMILIES ||--o{ PERSONS : contains
    FAMILIES ||--o{ NEEDS : reports
    RELIEF_ITEMS ||--o{ NEEDS : requested_as
    DONORS ||--o{ DONATIONS : gives
    RELIEF_ITEMS ||--o{ DONATIONS : received_as
    WAREHOUSES ||--o{ DONATIONS : receives
    WAREHOUSES ||--o{ STOCK : stores
    RELIEF_ITEMS ||--o{ STOCK : counted_in
    STOCK ||--o{ STOCK_MOVEMENTS : logs
    DONATIONS o|--|| STOCK_MOVEMENTS : receipt_source
    DISTRIBUTIONS o|--|| STOCK_MOVEMENTS : issue_source
    VOLUNTEERS ||--o{ ASSIGNMENTS : takes
    CAMPS ||--o{ ASSIGNMENTS : hosts
    NEEDS ||--o{ DISTRIBUTIONS : fulfilled_by
    STOCK ||--o{ DISTRIBUTIONS : supplied_from
    ASSIGNMENTS ||--o{ DISTRIBUTIONS : handled_by
    PERSONS ||--o{ REFERRALS : receives

    DISASTERS {
        int disaster_id PK
        string name
        string disaster_type
    }
    LOCATIONS {
        int location_id PK
        string district
        string area
    }
    CAMPS {
        int camp_id PK
        int disaster_id FK
        int location_id FK
        string name
        int capacity
    }
    FAMILIES {
        int family_id PK
        int camp_id FK
        string registration_code UK
    }
    PERSONS {
        int person_id PK
        int family_id FK
        string full_name
    }
    RELIEF_ITEMS {
        int item_id PK
        string name
        string unit
    }
    NEEDS {
        int need_id PK
        int family_id FK
        int item_id FK
        string relief_round
        int quantity_required
        string urgency
    }
    DONORS {
        int donor_id PK
        string name
    }
    WAREHOUSES {
        int warehouse_id PK
        int location_id FK
        string name
    }
    DONATIONS {
        int donation_id PK
        int donor_id FK
        int warehouse_id FK
        int item_id FK
        int quantity_received
    }
    STOCK {
        int warehouse_id PK,FK
        int item_id PK,FK
        int quantity_on_hand
    }
    STOCK_MOVEMENTS {
        int movement_id PK
        int warehouse_id FK
        int item_id FK
        string movement_type
        int quantity_change
        int donation_id FK
        int distribution_id FK
    }
    VOLUNTEERS {
        int volunteer_id PK
        string full_name
    }
    ASSIGNMENTS {
        int assignment_id PK
        int volunteer_id FK
        int camp_id FK
        datetime starts_at
        datetime ends_at
    }
    DISTRIBUTIONS {
        int distribution_id PK
        int need_id FK
        int warehouse_id FK
        int item_id FK
        int assignment_id FK
        string request_token UK
        int quantity_issued
    }
    REFERRALS {
        int referral_id PK
        int person_id FK
        string destination
        string status
    }
```

`STOCK` is identified by the pair `(warehouse_id, item_id)`. A distribution uses the stock row for the requested item's `item_id` and selected warehouse. The database transaction will check this relationship and write the corresponding `STOCK_MOVEMENTS` row.

The `ASSIGNMENTS` link records which scheduled volunteer handled a distribution. The application will check that the assignment belongs to the family's camp and is active at the distribution time.
