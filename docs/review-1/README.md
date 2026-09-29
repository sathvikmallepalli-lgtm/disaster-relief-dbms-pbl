# Review 1 · Problem and Conceptual Design

## Problem

During disaster response, separate paper or spreadsheet lists for camps, families, needs, donated supplies, and distributions make it hard to know who has received what. Duplicate entries can cause repeated distributions, while missing stock information can leave urgent needs unmet. A small, consistent database can help a local relief team coordinate one disaster response without claiming to replace professional emergency systems.

## Objective

Design a relational database that records people and camps, item needs, incoming supplies, stock, volunteers, distributions, and referrals. The eventual application should let staff answer three immediate questions: **Who needs help? What supplies are available? What has already been given?**

## Users

| User | Main task |
| --- | --- |
| Relief coordinator | Review unmet needs, camp summaries, and distribution records |
| Camp worker | Register families and persons, assess needs, record referrals |
| Warehouse worker | Record donations, receipts, and available stock |
| Volunteer coordinator | Schedule volunteers and review work history |

For the student MVP, these are functional roles. Advanced login and permissions are outside the initial scope.

## Scope

The system covers disaster and camp records; family and person registration; item needs by relief round; donation receipts; warehouse stock; volunteer assignments; distributions; referrals; and basic reports. It is intended for one local relief operation with fictional demonstration data.

It does not cover GPS tracking, prediction, automated eligibility decisions, online payment processing, or live emergency dispatch.

## Functional requirements

| ID | Requirement | Review 3 demonstration |
| --- | --- | --- |
| FR-01 | Create and find disasters, locations, and camps | Select a camp for a disaster |
| FR-02 | Register a family and its members at a camp | Search a family by registration code |
| FR-03 | Assess an item need with quantity, urgency, and relief round | Show it in unmet needs |
| FR-04 | Record a donor's item receipt into a warehouse | Stock balance increases and receipt is traceable |
| FR-05 | Assign a volunteer to a camp for a time interval | Reject overlapping assignments |
| FR-06 | Distribute an item against a recorded need | Reject duplicate request, excess quantity, or insufficient stock |
| FR-07 | Record a person's referral and status | Find open referrals |
| FR-08 | Produce useful summaries | Camp population, unmet needs, stock, distributions, donors, volunteer work, referrals |

## Data and integrity rules

- Every camp belongs to one disaster and one location. A family has one current camp; each person belongs to one family.
- A need belongs to one family, one relief item, and one relief round. A family cannot have two need records for the same item in the same round.
- Required, received, and distributed quantities must be positive. Stock balances cannot be negative.
- A repeated submission of the same distribution event must not be processed twice. The sum of distributions for a need must not exceed its required quantity.
- A volunteer cannot be assigned to overlapping intervals. Each assignment has a valid start and end.
- Receipts and issues change stock in a transaction and create a movement record, so stock history is explainable.

## Conceptual design

The [ER diagram](erd.md) shows the entities and their cardinalities. The [initial schema](schema.md) maps them to tables, primary keys, and foreign keys. This is a proposed design; column types, exact constraints, and 3NF justification belong to Review 2.

## Review 1 evidence checklist

- [x] Problem, objective, users, and scope
- [x] Functional requirements and business rules
- [x] Conceptual ER diagram for all principal assignment entities
- [x] Initial relational schema with primary and foreign keys
- [x] [Presentation walkthrough](walkthrough.md)
