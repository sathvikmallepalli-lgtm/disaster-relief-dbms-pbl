# Disaster Relief Resource and Camp Management System

**DBMS Project Based Learning · Project 60**

Relief teams often track camp residents, requested supplies, donations, stock, and distributions in separate registers. This project designs one relational database so a team can see what each family still needs, what is available, and what has already been issued.

The distinctive feature is a **transparent unmet-needs queue**: urgent requests appear first, then older requests. The database prototype will check distributions against recorded need and available stock, and make every stock change traceable. This uses ordinary relational design, SQL queries, constraints, and transactions.

**Chosen stack:** MySQL database and a small Python application. The design uses basic forms and reports; it does not require AI, maps, or cloud services.

## Review progress

| Review | Due in assignment | Evidence | Status |
| --- | --- | --- | --- |
| 1 · Design | Week 7 · 5 marks | Problem, scope, requirements, ERD, initial relational schema | Ready for discussion |
| 2 · Database prototype | Week 11 · 5 marks | 3NF, data dictionary, DDL, sample data, SQL reports, prototype | Planned |
| 3 · Application | Week 16 · 5 marks | Python app, CRUD, validation, reports, screenshots, final report, viva | Planned |

Start with the [Review 1 evidence](docs/review-1/README.md). The [review roadmap](docs/roadmap.md) lists what will be added at each stage.

## Core workflow

1. Register a disaster, camp, family, and family members.
2. Record a family's item needs and urgency for a relief round.
3. Receive donated items into a warehouse and record stock movement.
4. Assign volunteers to camps without overlapping time slots.
5. Issue items against a recorded need, within the remaining need and stock balance.
6. View unmet needs, camp population, stock, distribution history, donor contributions, volunteer work, and referrals.

## Repository map

```text
docs/
  roadmap.md             Review-by-review evidence plan
  review-1/
    README.md            Problem, scope, users, requirements, rules
    erd.md               Conceptual ER diagram
    schema.md            Initial relational schema
    walkthrough.md       Short presentation walkthrough
```

The database scripts and application will be added for their respective reviews. All example names and records will be fictional.

## Assignment source

Project 60 in `DBMS_PBL_70_Unique_Project_Statements.docx`: “Design and Implementation of a Database Management System for Disaster Relief Resource and Camp Management System.” The assignment permits MySQL, PostgreSQL, or Oracle for the database and Java or Python for the application. This project uses MySQL and Python.
