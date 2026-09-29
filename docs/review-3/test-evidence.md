# Test Evidence

The following checks were run on a fresh, disposable MySQL database named `dbms_pbl_test_run4` after loading `database/schema.sql` and `database/seed.sql`.

```text
python -m unittest discover -s tests -v
test_concurrent_issues_cannot_exceed_need ... ok
test_distribution_rejects_duplicate_and_excess ... ok
test_duplicate_assessment_is_rejected ... ok
test_overlapping_volunteer_assignment_is_rejected ... ok
test_receipt_increases_stock_and_records_movement ... ok
test_stock_matches_movement_ledger ... ok
test_web_family_registration_and_assessment ... ok
test_web_pages_and_catalogue_crud ... ok

Ran 8 tests
OK
```

The database report script also ran after the tests. The ledger reconciliation query returned no mismatched stock rows. A browser walkthrough submitted a three-kit distribution, then showed the remaining need as two and the warehouse water-kit stock as seventeen.
