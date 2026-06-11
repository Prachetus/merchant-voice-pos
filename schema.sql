-- 1. Create the database
CREATE DATABASE IF NOT EXISTS voice_pos_db;
USE voice_pos_db;

-- 2. Create the inventory table
CREATE TABLE IF NOT EXISTS inventory (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    reorder_threshold INT NOT NULL DEFAULT 5,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Insert initial fast-moving catalog data
-- We are keeping the item names aligned with how a merchant might naturally speak them.
INSERT INTO inventory (item_name, stock, reorder_threshold) VALUES
('packets of milk', 50, 10),
('loaf of bread', 30, 5),
('packets of sugar', 100, 20),
('packets of chips', 80, 15),
('bottles of water', 60, 10),
('kilograms of rice', 200, 50),
('kilograms of dal', 100, 20),
('packets of biscuits', 120, 30),
('bars of soap', 75, 15),
('tubes of toothpaste', 40, 10);