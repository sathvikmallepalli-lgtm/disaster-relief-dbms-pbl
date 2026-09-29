-- Fictional demonstration records. Run once after schema.sql.
INSERT INTO disasters (disaster_id, name, disaster_type, started_on) VALUES
  (1, 'North River Flood', 'Flood', '2026-09-20');

INSERT INTO locations (location_id, district, area, state) VALUES
  (1, 'Demo District', 'River Ward', 'Demo State'),
  (2, 'Demo District', 'Central Ward', 'Demo State');

INSERT INTO camps (camp_id, disaster_id, location_id, name, capacity, opened_on) VALUES
  (1, 1, 1, 'Riverside School Camp', 120, '2026-09-21'),
  (2, 1, 2, 'Central Hall Camp', 90, '2026-09-22');

INSERT INTO families (family_id, camp_id, registration_code) VALUES
  (1, 1, 'F-001'),
  (2, 1, 'F-002'),
  (3, 2, 'F-003');

INSERT INTO persons (person_id, family_id, full_name, age_at_registration, relationship_to_head) VALUES
  (1, 1, 'Asha Rao', 34, 'Head'),
  (2, 1, 'Ravi Rao', 36, 'Spouse'),
  (3, 1, 'Mira Rao', 8, 'Child'),
  (4, 1, 'Kiran Rao', 5, 'Child'),
  (5, 2, 'Farah Khan', 41, 'Head'),
  (6, 2, 'Imran Khan', 13, 'Child'),
  (7, 3, 'Neha Das', 29, 'Head');

INSERT INTO relief_items (item_id, name, unit, category) VALUES
  (1, 'Water kit', 'kit', 'Water'),
  (2, 'Food kit', 'kit', 'Food'),
  (3, 'Blanket', 'piece', 'Shelter');

INSERT INTO needs (need_id, family_id, item_id, relief_round, quantity_required, urgency) VALUES
  (1, 1, 1, '2026-W01', 5, 'HIGH'),
  (2, 1, 2, '2026-W01', 3, 'MEDIUM'),
  (3, 2, 1, '2026-W01', 2, 'HIGH'),
  (4, 3, 3, '2026-W01', 4, 'LOW');

INSERT INTO donors (donor_id, name, contact) VALUES
  (1, 'Community Aid Group', NULL),
  (2, 'Local College Volunteers', NULL);

INSERT INTO warehouses (warehouse_id, location_id, name) VALUES
  (1, 2, 'Central Relief Store');

INSERT INTO donations (donation_id, donor_id, warehouse_id, item_id, quantity_received, receipt_token) VALUES
  (1, 1, 1, 1, 20, '00000000-0000-4000-8000-000000000001'),
  (2, 2, 1, 2, 12, '00000000-0000-4000-8000-000000000002'),
  (3, 1, 1, 3, 10, '00000000-0000-4000-8000-000000000003');

INSERT INTO stock (warehouse_id, item_id, quantity_on_hand) VALUES
  (1, 1, 20), (1, 2, 12), (1, 3, 10);

INSERT INTO volunteers (volunteer_id, full_name, phone) VALUES
  (1, 'Arun Mehta', NULL),
  (2, 'Leena Joseph', NULL);

INSERT INTO assignments (assignment_id, volunteer_id, camp_id, starts_at, ends_at) VALUES
  (1, 1, 1, NOW() - INTERVAL 1 DAY, NOW() + INTERVAL 30 DAY),
  (2, 2, 2, NOW() - INTERVAL 1 DAY, NOW() + INTERVAL 30 DAY);

INSERT INTO stock_movements (movement_id, warehouse_id, item_id, movement_type, quantity_change, donation_id) VALUES
  (1, 1, 1, 'RECEIPT', 20, 1),
  (2, 1, 2, 'RECEIPT', 12, 2),
  (3, 1, 3, 'RECEIPT', 10, 3);

INSERT INTO referrals (referral_id, person_id, destination, reason) VALUES
  (1, 3, 'Camp medical desk', 'Routine health check');
