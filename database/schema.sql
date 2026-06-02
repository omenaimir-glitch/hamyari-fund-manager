-- طرح پایگاه داده صندوق همیاری

-- جدول مسئولان صندوق
CREATE TABLE IF NOT EXISTS managers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('admin', 'moderator') DEFAULT 'moderator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول اعضا
CREATE TABLE IF NOT EXISTS members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    national_id VARCHAR(20) UNIQUE,
    join_date DATE NOT NULL,
    status ENUM('active', 'inactive', 'blocked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
);

-- جدول تنظیمات شارژ سالیانه
CREATE TABLE IF NOT EXISTS annual_charges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    year INT NOT NULL,
    charge_amount DECIMAL(12, 2) NOT NULL,
    effective_from DATE NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_year (year),
    FOREIGN KEY (created_by) REFERENCES managers(id),
    INDEX idx_year (year)
);

-- جدول شارژ‌های ماهانه اعضا
CREATE TABLE IF NOT EXISTS member_charges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE,
    status ENUM('pending', 'paid', 'overdue') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member_month (member_id, month, year),
    INDEX idx_member (member_id),
    INDEX idx_status (status)
);

-- جدول وام‌ها
CREATE TABLE IF NOT EXISTS loans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    loan_date DATE NOT NULL,
    start_repayment DATE NOT NULL,
    end_repayment DATE NOT NULL,
    monthly_payment DECIMAL(12, 2) NOT NULL,
    total_remaining DECIMAL(12, 2) NOT NULL,
    status ENUM('active', 'completed', 'overdue', 'cancelled') DEFAULT 'active',
    queue_position INT,
    approved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES managers(id),
    INDEX idx_member (member_id),
    INDEX idx_status (status),
    INDEX idx_queue (queue_position)
);

-- جدول پرداخت‌های وام
CREATE TABLE IF NOT EXISTS loan_payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    installment_number INT NOT NULL,
    payment_date DATE,
    amount DECIMAL(12, 2) NOT NULL,
    status ENUM('pending', 'paid', 'overdue') DEFAULT 'pending',
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE,
    UNIQUE KEY unique_loan_installment (loan_id, installment_number),
    INDEX idx_loan (loan_id),
    INDEX idx_status (status)
);

-- جدول موجودی صندوق (آرشیو روزانه)
CREATE TABLE IF NOT EXISTS fund_balance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL UNIQUE,
    total_balance DECIMAL(14, 2) NOT NULL,
    total_charges DECIMAL(14, 2) NOT NULL,
    total_active_loans DECIMAL(14, 2) NOT NULL,
    available_balance DECIMAL(14, 2) NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (date)
);

-- جدول سابقه تغییرات
CREATE TABLE IF NOT EXISTS activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    old_value TEXT,
    new_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES managers(id),
    INDEX idx_user (user_id),
    INDEX idx_action (action_type),
    INDEX idx_date (created_at)
);

-- جدول صف انتظار وام
CREATE TABLE IF NOT EXISTS loan_queue (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    requested_amount DECIMAL(12, 2),
    queue_position INT NOT NULL,
    request_date DATE NOT NULL,
    status ENUM('waiting', 'approved', 'rejected', 'cancelled') DEFAULT 'waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member_queue (member_id),
    INDEX idx_position (queue_position),
    INDEX idx_status (status)
);

-- ایندکس‌های اضافی برای کارایی
CREATE INDEX idx_charges_year_member ON member_charges(year, member_id);
CREATE INDEX idx_loans_date ON loans(loan_date);
CREATE INDEX idx_payments_date ON loan_payments(payment_date);