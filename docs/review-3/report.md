# Project 60 Final Report

## Abstract

The Disaster Relief Resource and Camp Management System is a small MySQL and Python application for recording camp residents, assessed item needs, donated supplies, warehouse stock, volunteers, distributions, and referrals. It addresses duplication and poor visibility caused by separate manual registers. A transparent queue lists unmet needs by stated urgency and assessment time. The application checks each issue against remaining need and available stock and records a stock movement for every receipt or issue.

## Problem and objectives

Relief workers need to answer who is registered, what each family still needs, what is available, and what has been issued. Manual lists can repeat the same family or entitlement and make stock reconciliation difficult. The project objective is a relational database with integrity constraints, a basic connected application, and useful reports that support staff decisions.

The system is intended as a local educational demonstration with fictional data. It does not automate allocation decisions or replace operational disaster-response software.

## Requirements and design

The design covers the 14 principal entities in the assignment: disasters, locations, camps, families, persons, needs, relief items, warehouses, stock, donations, volunteers, assignments, distributions, and referrals. Donors and stock movements are added for donor reporting and audit history. The [Review 1 ER diagram](../review-1/erd.md) shows the relationships; the [implemented MySQL schema](../../database/schema.sql) gives column types and keys.

The main relationships are one disaster to many camps, one camp to many families, one family to many people and needs, one need to many partial distributions, and one warehouse/item pair to one current stock balance. Each distribution points to a volunteer assignment and is handled within a transaction. The Review 1 proposal contained an item ID on distributions; the Review 2 implementation derives that item from the need to avoid storing it twice.

## Database design

The schema uses primary keys, foreign keys, unique constraints, non-null fields, checks, defaults, and indexes. The [normalization notes](../review-2/normalization.md) list the functional dependencies and explain the 3NF decomposition. `stock` is an operational balance and `stock_movements` is an append-only audit log. Their limited duplication is intentional and is reconciled by a query.

Important rules include one need per family/item/relief round; positive quantities; a unique token for each receipt and distribution request; no overlapping assignments; no issue above remaining need; and no issue above stock. Constraints handle single-row rules. Python transactions use `READ COMMITTED` and lock the relevant volunteer, need, and stock rows before checking rules that span rows. Receipt or issue changes and the matching movement are committed together.

Seven SQL views provide camp population, unmet needs, stock, distribution history, donor contributions, volunteer work, and open referrals. The [query file](../../database/reports.sql) demonstrates joins, a nested query, aggregation, views, and ledger reconciliation.

## Application and innovation

The Python application presents basic forms and tables for family registration, needs assessment, donation receipt, volunteer assignment, distribution, referral, item CRUD, search, and reports. It runs locally and connects directly to MySQL. Invalid submissions show a useful message and the transaction rolls back.

The innovation is modest and explainable: the unmet-needs queue sorts by **urgency**, then **assessment time**, while the remaining quantity comes from assessed need minus past distributions. It helps a coordinator review requests without hiding the rule behind a complex algorithm. The stock ledger helps explain how a balance changed.

## Demonstration results

The fictional seed contains one flood, two camps, three families, seven people, four needs, three relief items, one warehouse, two volunteers, and a referral. The SQL reports initially show 20 water kits. In a demonstrated issue of three kits to family `F-001`, the remaining need changes from five to two and water-kit stock changes from 20 to 17. The distribution history identifies the family, volunteer, and warehouse. A duplicate request and an issue above the remaining need are rejected. The screenshots in the [Review 3 guide](README.md#output-screens) show the interface and report output.

Eight integration tests passed on a newly created MySQL database. They cover concurrent issues, duplicate assessment and receipts, donation receipt and movement, duplicate, excess, and wrong-camp distribution, overlapping volunteer assignment, stock reconciliation, family registration and assessment through the app, application pages, form protection, and item CRUD. The [test evidence](test-evidence.md) records the command and result.

## Limits and next improvements

The first version uses fictional data and a local trusted operator. It has no user login, offline synchronization, or cross-camp family transfer history. A later version could add explicit user permissions and transfer records if a real relief organization defined those requirements. The current project keeps the workflow small enough to demonstrate database design and integrity clearly.
