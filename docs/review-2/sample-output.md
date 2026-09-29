# Sample Database Query Output

These values were checked on the fictional seed. Timestamps depend on when `seed.sql` is loaded, so they are omitted here. The [report queries](../../database/reports.sql) reproduce the full rows.

## Before a distribution

| Camp | Families | People |
| --- | ---: | ---: |
| Central Hall Camp | 1 | 1 |
| Riverside School Camp | 2 | 6 |

| Family | Item | Urgency | Required | Issued | Remaining |
| --- | --- | --- | ---: | ---: | ---: |
| F-001 | Water kit | HIGH | 5 | 0 | 5 |
| F-002 | Water kit | HIGH | 2 | 0 | 2 |
| F-001 | Food kit | MEDIUM | 3 | 0 | 3 |
| F-003 | Blanket | LOW | 4 | 0 | 4 |

| Item | Warehouse stock |
| --- | ---: |
| Water kit | 20 |
| Food kit | 12 |
| Blanket | 10 |

The nested query for assessments above that item's average returns **F-001, Water kit, 5**. The stock reconciliation query returns no rows because all balances match their receipt movements.

## After issuing three water kits to F-001

| Check | Result |
| --- | --- |
| F-001 water kits remaining | 2 |
| Water kits in warehouse | 17 |
| Distribution history | F-001 received 3 water kits from Central Relief Store, handled by Arun Mehta |
| Stock movement | `ISSUE`, quantity change `-3` |
| Ledger reconciliation | No mismatched rows |

Repeating the same distribution token is rejected. An additional issue of three is also rejected because the need has only two kits remaining.
