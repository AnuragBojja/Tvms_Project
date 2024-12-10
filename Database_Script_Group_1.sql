-- Create the database
CREATE DATABASE IF NOT EXISTS TVMS;

-- Use the created database
USE TVMS;
-- Create audit_logs table
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    super_user_id INT,
    action_type VARCHAR(50),
    table_name VARCHAR(100),
    record_id INT,
    timestamp DATETIME,
    description TEXT
);


-- Create incidents table
CREATE TABLE incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    violator_id INT,
    officer_id INT,
    violation_type VARCHAR(100),
    violation_category ENUM('Traffic', 'Parking'),
    description TEXT,
    location VARCHAR(255),
    date_time DATETIME,
    violator_first_name VARCHAR(255),
    violator_middle_name VARCHAR(255),
    violator_last_name VARCHAR(255),
    driver_license VARCHAR(100),
    log_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create vehicle_records table with foreign key
CREATE TABLE vehicle_records (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id INT,
    make VARCHAR(50),
    model VARCHAR(50),
    color VARCHAR(50),
    license_plate VARCHAR(20),
    log_id INT,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
);

-- Create fines table with foreign key
CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number VARCHAR(10),
    incident_id INT,
    officer_determined_amount DECIMAL(10, 2),
    due_date DATE,
    paid_status VARCHAR(50),
    log_id INT,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
);

-- Create officers table
CREATE TABLE officers (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    badge_number VARCHAR(100),
    precinct VARCHAR(100),
    contact_info VARCHAR(255),
    password VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(15),
    log_id INT
);

-- Create payments table with foreign key
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    fine_id INT,
    amount_paid DECIMAL(10, 2),
    payment_date DATETIME,
    payment_method VARCHAR(100),
    log_id INT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    card_type VARCHAR(50),
    card_number VARCHAR(16),
    expiry_date DATE,
    cvv INT,
    card_holder_name VARCHAR(255),
    billing_address TEXT,
    FOREIGN KEY (fine_id) REFERENCES fines(fine_id) ON DELETE CASCADE
);

-- Create super_users table
CREATE TABLE super_users (
    super_user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    phone_number VARCHAR(15),
    email VARCHAR(255),
    password VARCHAR(255),
    role ENUM('admin', 'manager'),
    contact_info VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create violators table
CREATE TABLE violators (
    violator_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    address VARCHAR(255),
    license_number VARCHAR(100),
    contact_info VARCHAR(255),
    phone_number VARCHAR(15),
    email VARCHAR(255),
    password VARCHAR(255),
    log_id INT
);

CREATE TABLE court_cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id INT,
    court_date DATE,
    judge_id INT,
    outcome VARCHAR(255),
    log_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
);
CREATE TABLE schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    event_type VARCHAR(50),
    scheduled_date DATETIME,
    location VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (case_id) REFERENCES court_cases(case_id) ON DELETE CASCADE
);
-- Add foreign key constraints to incidents table
ALTER TABLE incidents
ADD FOREIGN KEY (violator_id) REFERENCES violators(violator_id) ON DELETE RESTRICT,
ADD FOREIGN KEY (officer_id) REFERENCES officers(officer_id) ON DELETE RESTRICT,
ADD FOREIGN KEY (log_id) REFERENCES audit_logs(log_id) ON DELETE RESTRICT;
