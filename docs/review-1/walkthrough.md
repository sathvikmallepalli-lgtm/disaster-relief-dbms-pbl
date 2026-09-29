# Review 1 Presentation Walkthrough

Use this short fictional example to explain the design to a reviewer. No real beneficiary data is needed.

1. A flood is recorded as a disaster. A school building is recorded as a camp at a location.
2. Family `F-001` is registered at that camp with four persons.
3. A camp worker assesses the family for five water kits in relief round `2026-W01`, with high urgency.
4. A donor supplies twenty water kits to a warehouse. The receipt raises stock and creates a stock movement.
5. A volunteer is assigned to the camp. The worker issues three kits against `F-001`'s need.
6. The remaining need is two kits; the warehouse now has seventeen. A repeated request token must not issue another three kits.
7. The coordinator can see `F-001` on the unmet-needs report, the donation in the donor report, and the issue in the distribution and stock movement history.

## Questions to be ready for

**Why a separate `persons` table?** A family can have many members; storing names in one family field would prevent reliable counting and referrals to a particular person.

**Why separate `needs` from `distributions`?** An assessment records what is required; distributions record what was actually supplied. The difference identifies unmet need.

**Why keep both `stock` and `stock_movements`?** `stock` supports fast current balance checks. The movement log explains how that balance changed and supports auditing.

**How will duplicate or excess distributions be stopped?** The unique family/item/round need key prevents duplicate assessments. A unique request token handles accidental resubmission. A transaction checks cumulative issued quantity and stock before inserting a distribution and updating stock.

**Where is the innovation?** The unmet-needs queue ranks recorded requests using explicit urgency and waiting time. It is explainable with a SQL query and does not make decisions automatically.
