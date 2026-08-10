-- Military Medical Logistics Data Architecture
-- ANA 320: Data Management Schema Implementation

-- 1. Supply Items Catalog Table
CREATE TABLE IF NOT EXISTS supply_catalog (
    item_nsn VARCHAR(13) PRIMARY KEY, -- National Stock Number
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    is_perishable BOOLEAN DEFAULT FALSE,
    required_temp_celsius DECIMAL(4, 2) NULL
);

-- 2. Storage Locations / Facilities Table
CREATE TABLE IF NOT EXISTS storage_facilities (
    facility_id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL,
    location_code VARCHAR(20) NOT NULL,
    climate_controlled BOOLEAN DEFAULT TRUE
);

-- 3. Inventory Stock Table
CREATE TABLE IF NOT EXISTS inventory_levels (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    item_nsn VARCHAR(13) NOT NULL,
    facility_id INT NOT NULL,
    quantity_on_hand INT NOT NULL CHECK (quantity_on_hand >= 0),
    expiration_date DATE NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (item_nsn) REFERENCES supply_catalog(item_nsn) ON DELETE RESTRICT,
    FOREIGN KEY (facility_id) REFERENCES storage_facilities(facility_id) ON DELETE RESTRICT
);

-- Index for high-density query retrieval
CREATE INDEX idx_inventory_nsn ON inventory_levels(item_nsn);
CREATE INDEX idx_inventory_facility ON inventory_levels(facility_id);
