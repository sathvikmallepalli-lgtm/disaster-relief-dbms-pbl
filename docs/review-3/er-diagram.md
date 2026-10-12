# Final ER Diagram

This diagram matches the implemented MySQL tables in [`database/schema.sql`](../../database/schema.sql). PK means primary key, FK means foreign key, and UK means unique key. Each `STOCK` row is identified by its warehouse and item together.

The distribution's item comes from its linked `NEEDS` row. The Python transaction checks that the chosen warehouse has stock for that same item. One donation or distribution has one matching stock movement; `STOCK_MOVEMENTS` keeps both source IDs optional because a movement is either a receipt or an issue.

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
    WAREHOUSES ||--o{ DONATIONS : receives
    RELIEF_ITEMS ||--o{ DONATIONS : received_as
    WAREHOUSES ||--o{ STOCK : stores
    RELIEF_ITEMS ||--o{ STOCK : counted_in
    VOLUNTEERS ||--o{ ASSIGNMENTS : takes
    CAMPS ||--o{ ASSIGNMENTS : hosts
    NEEDS ||--o{ DISTRIBUTIONS : fulfilled_by
    WAREHOUSES ||--o{ DISTRIBUTIONS : supplies
    ASSIGNMENTS ||--o{ DISTRIBUTIONS : handles
    STOCK ||--o{ STOCK_MOVEMENTS : logs
    DONATIONS o|--o| STOCK_MOVEMENTS : receipt_source
    DISTRIBUTIONS o|--o| STOCK_MOVEMENTS : issue_source
    PERSONS ||--o{ REFERRALS : receives

    DISASTERS {
      int disaster_id PK
    }
    LOCATIONS {
      int location_id PK
    }
    CAMPS {
      int camp_id PK
      int disaster_id FK
      int location_id FK
    }
    FAMILIES {
      int family_id PK
      int camp_id FK
      string registration_code UK
    }
    PERSONS {
      int person_id PK
      int family_id FK
    }
    RELIEF_ITEMS {
      int item_id PK
    }
    NEEDS {
      int need_id PK
      int family_id FK
      int item_id FK
      string relief_round
    }
    DONORS {
      int donor_id PK
    }
    WAREHOUSES {
      int warehouse_id PK
      int location_id FK
    }
    DONATIONS {
      int donation_id PK
      int donor_id FK
      int warehouse_id FK
      int item_id FK
    }
    STOCK {
      int warehouse_id PK,FK
      int item_id PK,FK
    }
    VOLUNTEERS {
      int volunteer_id PK
    }
    ASSIGNMENTS {
      int assignment_id PK
      int volunteer_id FK
      int camp_id FK
    }
    DISTRIBUTIONS {
      int distribution_id PK
      int need_id FK
      int warehouse_id FK
      int assignment_id FK
    }
    STOCK_MOVEMENTS {
      int movement_id PK
      int warehouse_id FK
      int item_id FK
      int donation_id FK
      int distribution_id FK
    }
    REFERRALS {
      int referral_id PK
      int person_id FK
    }
```
