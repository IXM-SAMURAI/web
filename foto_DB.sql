-- Этот код выполняем в SQL-редакторе phpMyAdmin
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    duration INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_special_offer BOOLEAN DEFAULT FALSE,
    discount_percent INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);