# Viva Notes

These answers describe the actual implementation and can be practiced with the app open.

| Question | Short answer |
| --- | --- |
| What is the difference between a primary and foreign key? | A primary key uniquely identifies a row in its table. A foreign key requires a reference to an existing row in another table. For example, `families.family_id` is a PK and `families.camp_id` is an FK. |
| Why have separate family and person tables? | One family has many people. Separate rows avoid repeating family details for every person and allow a referral to identify one person. |
| Why separate needs and distributions? | A need is the assessed quantity. A distribution is what was actually issued. Their difference is the unmet quantity. One need can receive several partial issues. |
| What prevents duplicate entitlement records? | `UNIQUE (family_id, item_id, relief_round)` on `needs`. A unique distribution request token also stops the same submission being processed twice. |
| Why is a simple `CHECK` insufficient for maximum distribution? | The maximum depends on the sum of several distribution rows. A row-level check cannot compare that total. The transaction locks the need row and checks the sum before inserting. |
| How is negative stock prevented? | The transaction locks the warehouse/item stock row and decrements only if enough remains. The table also has a nonnegative `CHECK`. |
| How are overlapping assignments prevented? | The transaction locks the volunteer row, searches for an interval with `existing.start < new.end` and `existing.end > new.start`, and rejects an overlap. |
| What is 3NF here? | Each core entity table keeps facts determined by its key, and descriptive fields are not copied into unrelated tables. The operational stock balance and audit log are explained exceptions. |
| What is a view? | A saved query that presents a useful result without copying the source rows. `v_unmet_needs` joins family, item, and distribution data to calculate remaining need. |
| Why use an index? | It speeds repeated lookups. The needs queue and volunteer interval search have indexes on their search fields. Indexes cost some space and write time, so only frequent searches are indexed. |
| Why use a transaction? | Receipt or issue requires several changes. A transaction commits all of them together or rolls them all back on failure. |
| What is the practical innovation? | The queue gives a transparent order for reviewing unmet needs, and the movement history lets staff reconcile stock. Both use basic SQL and explicit rules. |
