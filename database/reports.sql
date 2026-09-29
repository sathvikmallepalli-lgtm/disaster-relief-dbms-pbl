-- Run these examples after schema.sql and seed.sql.

-- JOIN + aggregation: population at each camp.
SELECT * FROM v_camp_population ORDER BY camp_name;

-- VIEW + ordered priority queue: urgency first, then oldest request.
SELECT * FROM v_unmet_needs
ORDER BY FIELD(urgency, 'HIGH', 'MEDIUM', 'LOW'), assessed_at, need_id;

-- JOIN: warehouse stock with item names.
SELECT * FROM v_stock ORDER BY warehouse_name, item_name;

-- JOIN: trace each issue to a family, volunteer, and warehouse.
SELECT * FROM v_distribution_history ORDER BY issued_at DESC;

-- AGGREGATION: donor totals by item.
SELECT * FROM v_donor_contributions ORDER BY donor_name, item_name;

-- JOIN + aggregation: volunteer assignment workload.
SELECT * FROM v_volunteer_work ORDER BY volunteer_name, starts_at;

-- JOIN: referrals still waiting for follow-up.
SELECT * FROM v_open_referrals ORDER BY referred_at;

-- SUBQUERY: assessments above the average requested quantity for that item.
SELECT f.registration_code, i.name AS item_name, n.quantity_required
FROM needs n
JOIN families f ON f.family_id = n.family_id
JOIN relief_items i ON i.item_id = n.item_id
WHERE n.quantity_required > (
    SELECT AVG(n2.quantity_required)
    FROM needs n2 WHERE n2.item_id = n.item_id
  );

-- Stock ledger reconciliation: should return zero rows.
SELECT s.warehouse_id, s.item_id, s.quantity_on_hand,
       COALESCE(SUM(m.quantity_change), 0) AS movement_total
FROM stock s
LEFT JOIN stock_movements m
  ON m.warehouse_id = s.warehouse_id AND m.item_id = s.item_id
GROUP BY s.warehouse_id, s.item_id, s.quantity_on_hand
HAVING s.quantity_on_hand <> movement_total;
