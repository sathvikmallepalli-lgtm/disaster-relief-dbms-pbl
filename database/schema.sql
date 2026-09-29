-- Project 60: Disaster Relief Resource and Camp Management System
-- Run this file inside a MySQL database created for this project.

CREATE TABLE disasters (
    disaster_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    disaster_type VARCHAR(60) NOT NULL,
    started_on DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT ck_disaster_status CHECK (status IN ('ACTIVE', 'CLOSED'))
);

CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    CONSTRAINT uq_location UNIQUE (district, area, state)
);

CREATE TABLE camps (
    camp_id INT AUTO_INCREMENT PRIMARY KEY,
    disaster_id INT NOT NULL,
    location_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    capacity INT NOT NULL,
    opened_on DATE NOT NULL,
    CONSTRAINT ck_camp_capacity CHECK (capacity > 0),
    CONSTRAINT uq_camp_name UNIQUE (disaster_id, name),
    CONSTRAINT fk_camp_disaster FOREIGN KEY (disaster_id) REFERENCES disasters (disaster_id),
    CONSTRAINT fk_camp_location FOREIGN KEY (location_id) REFERENCES locations (location_id)
);

CREATE TABLE families (
    family_id INT AUTO_INCREMENT PRIMARY KEY,
    camp_id INT NOT NULL,
    registration_code VARCHAR(30) NOT NULL UNIQUE,
    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT ck_family_status CHECK (status IN ('ACTIVE', 'LEFT')),
    CONSTRAINT fk_family_camp FOREIGN KEY (camp_id) REFERENCES camps (camp_id)
);

CREATE TABLE persons (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    age_at_registration INT NULL,
    relationship_to_head VARCHAR(40) NOT NULL,
    CONSTRAINT ck_person_age CHECK (age_at_registration IS NULL OR age_at_registration BETWEEN 0 AND 120),
    CONSTRAINT fk_person_family FOREIGN KEY (family_id) REFERENCES families (family_id)
);

CREATE TABLE relief_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    unit VARCHAR(30) NOT NULL,
    category VARCHAR(60) NOT NULL
);

CREATE TABLE needs (
    need_id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    item_id INT NOT NULL,
    relief_round VARCHAR(20) NOT NULL,
    quantity_required INT NOT NULL,
    urgency VARCHAR(10) NOT NULL,
    assessed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_need_quantity CHECK (quantity_required > 0),
    CONSTRAINT ck_need_urgency CHECK (urgency IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT uq_need_entitlement UNIQUE (family_id, item_id, relief_round),
    CONSTRAINT fk_need_family FOREIGN KEY (family_id) REFERENCES families (family_id),
    CONSTRAINT fk_need_item FOREIGN KEY (item_id) REFERENCES relief_items (item_id),
    INDEX idx_need_queue (urgency, assessed_at)
);

CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    contact VARCHAR(120) NULL
);

CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    name VARCHAR(120) NOT NULL UNIQUE,
    CONSTRAINT fk_warehouse_location FOREIGN KEY (location_id) REFERENCES locations (location_id)
);

CREATE TABLE donations (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity_received INT NOT NULL,
    received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    receipt_token CHAR(36) NOT NULL UNIQUE,
    CONSTRAINT ck_donation_quantity CHECK (quantity_received > 0),
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id) REFERENCES donors (donor_id),
    CONSTRAINT fk_donation_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
    CONSTRAINT fk_donation_item FOREIGN KEY (item_id) REFERENCES relief_items (item_id)
);

CREATE TABLE stock (
    warehouse_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    PRIMARY KEY (warehouse_id, item_id),
    CONSTRAINT ck_stock_nonnegative CHECK (quantity_on_hand >= 0),
    CONSTRAINT fk_stock_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
    CONSTRAINT fk_stock_item FOREIGN KEY (item_id) REFERENCES relief_items (item_id)
);

CREATE TABLE volunteers (
    volunteer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NULL
);

CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    camp_id INT NOT NULL,
    starts_at DATETIME NOT NULL,
    ends_at DATETIME NOT NULL,
    CONSTRAINT ck_assignment_time CHECK (ends_at > starts_at),
    CONSTRAINT fk_assignment_volunteer FOREIGN KEY (volunteer_id) REFERENCES volunteers (volunteer_id),
    CONSTRAINT fk_assignment_camp FOREIGN KEY (camp_id) REFERENCES camps (camp_id),
    INDEX idx_assignment_overlap (volunteer_id, starts_at, ends_at)
);

CREATE TABLE distributions (
    distribution_id INT AUTO_INCREMENT PRIMARY KEY,
    need_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    assignment_id INT NOT NULL,
    request_token CHAR(36) NOT NULL UNIQUE,
    quantity_issued INT NOT NULL,
    issued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_distribution_quantity CHECK (quantity_issued > 0),
    CONSTRAINT fk_distribution_need FOREIGN KEY (need_id) REFERENCES needs (need_id),
    CONSTRAINT fk_distribution_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
    CONSTRAINT fk_distribution_assignment FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id)
);

CREATE TABLE stock_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id INT NOT NULL,
    item_id INT NOT NULL,
    movement_type VARCHAR(10) NOT NULL,
    quantity_change INT NOT NULL,
    donation_id INT NULL UNIQUE,
    distribution_id INT NULL UNIQUE,
    moved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_movement_source CHECK (
        (movement_type = 'RECEIPT' AND quantity_change > 0 AND donation_id IS NOT NULL AND distribution_id IS NULL)
        OR
        (movement_type = 'ISSUE' AND quantity_change < 0 AND distribution_id IS NOT NULL AND donation_id IS NULL)
    ),
    CONSTRAINT fk_movement_stock FOREIGN KEY (warehouse_id, item_id) REFERENCES stock (warehouse_id, item_id),
    CONSTRAINT fk_movement_donation FOREIGN KEY (donation_id) REFERENCES donations (donation_id),
    CONSTRAINT fk_movement_distribution FOREIGN KEY (distribution_id) REFERENCES distributions (distribution_id)
);

CREATE TABLE referrals (
    referral_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    destination VARCHAR(120) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    referred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    CONSTRAINT ck_referral_status CHECK (status IN ('OPEN', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT fk_referral_person FOREIGN KEY (person_id) REFERENCES persons (person_id)
);

CREATE VIEW v_camp_population AS
SELECT c.camp_id, c.name AS camp_name, d.name AS disaster_name,
       COUNT(DISTINCT f.family_id) AS family_count,
       COUNT(p.person_id) AS person_count
FROM camps c
JOIN disasters d ON d.disaster_id = c.disaster_id
LEFT JOIN families f ON f.camp_id = c.camp_id AND f.status = 'ACTIVE'
LEFT JOIN persons p ON p.family_id = f.family_id
GROUP BY c.camp_id, c.name, d.name;

CREATE VIEW v_unmet_needs AS
SELECT n.need_id, f.registration_code, c.name AS camp_name,
       i.name AS item_name, i.unit, n.relief_round, n.urgency,
       n.quantity_required, COALESCE(x.quantity_issued, 0) AS quantity_issued,
       n.quantity_required - COALESCE(x.quantity_issued, 0) AS remaining_quantity,
       n.assessed_at
FROM needs n
JOIN families f ON f.family_id = n.family_id
JOIN camps c ON c.camp_id = f.camp_id
JOIN relief_items i ON i.item_id = n.item_id
LEFT JOIN (
    SELECT need_id, SUM(quantity_issued) AS quantity_issued
    FROM distributions GROUP BY need_id
) x ON x.need_id = n.need_id
WHERE f.status = 'ACTIVE' AND n.quantity_required > COALESCE(x.quantity_issued, 0);

CREATE VIEW v_stock AS
SELECT w.warehouse_id, w.name AS warehouse_name, i.item_id,
       i.name AS item_name, i.unit, s.quantity_on_hand
FROM stock s
JOIN warehouses w ON w.warehouse_id = s.warehouse_id
JOIN relief_items i ON i.item_id = s.item_id;

CREATE VIEW v_distribution_history AS
SELECT d.distribution_id, d.issued_at, f.registration_code,
       c.name AS camp_name, i.name AS item_name, d.quantity_issued,
       i.unit, w.name AS warehouse_name, v.full_name AS volunteer_name
FROM distributions d
JOIN needs n ON n.need_id = d.need_id
JOIN families f ON f.family_id = n.family_id
JOIN camps c ON c.camp_id = f.camp_id
JOIN relief_items i ON i.item_id = n.item_id
JOIN warehouses w ON w.warehouse_id = d.warehouse_id
JOIN assignments a ON a.assignment_id = d.assignment_id
JOIN volunteers v ON v.volunteer_id = a.volunteer_id;

CREATE VIEW v_donor_contributions AS
SELECT r.donor_id, r.name AS donor_name, i.name AS item_name,
       i.unit, SUM(d.quantity_received) AS quantity_donated
FROM donations d
JOIN donors r ON r.donor_id = d.donor_id
JOIN relief_items i ON i.item_id = d.item_id
GROUP BY r.donor_id, r.name, i.item_id, i.name, i.unit;

CREATE VIEW v_volunteer_work AS
SELECT v.volunteer_id, v.full_name AS volunteer_name,
       a.assignment_id, c.name AS camp_name, a.starts_at, a.ends_at,
       COUNT(d.distribution_id) AS distributions_handled
FROM assignments a
JOIN volunteers v ON v.volunteer_id = a.volunteer_id
JOIN camps c ON c.camp_id = a.camp_id
LEFT JOIN distributions d ON d.assignment_id = a.assignment_id
GROUP BY v.volunteer_id, v.full_name, a.assignment_id, c.name, a.starts_at, a.ends_at;

CREATE VIEW v_open_referrals AS
SELECT r.referral_id, p.full_name AS person_name,
       f.registration_code, c.name AS camp_name,
       r.destination, r.reason, r.referred_at
FROM referrals r
JOIN persons p ON p.person_id = r.person_id
JOIN families f ON f.family_id = p.family_id
JOIN camps c ON c.camp_id = f.camp_id
WHERE r.status = 'OPEN';
