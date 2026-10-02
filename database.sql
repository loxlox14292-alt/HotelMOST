-- Только для отдельного локального учебного сервера MySQL.
-- Все записи и учётные данные ниже демонстрационные, не для production.
-- Замените demo-пароль перед импортом и задайте HOTEL_DB_PASSWORD при запуске.
CREATE DATABASE IF NOT EXISTS hotel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'hotel_course_admin'@'localhost' IDENTIFIED BY 'dev_only_change_me';
GRANT ALL PRIVILEGES ON hotel_db.* TO 'hotel_course_admin'@'localhost';
FLUSH PRIVILEGES;
USE hotel_db;

CREATE TABLE IF NOT EXISTS users (
  id_user INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash CHAR(64) NOT NULL,
  role ENUM('admin','manager','guest') NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rooms (
  id_room INT AUTO_INCREMENT PRIMARY KEY,
  room_number VARCHAR(10) NOT NULL UNIQUE,
  category VARCHAR(50) NOT NULL,
  capacity INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  status ENUM('free','occupied','cleaning','repair') NOT NULL DEFAULT 'free'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS guests (
  id_guest INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  passport VARCHAR(50) NOT NULL UNIQUE,
  phone VARCHAR(20) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS bookings (
  id_booking INT AUTO_INCREMENT PRIMARY KEY,
  check_in_date DATE NOT NULL,
  check_out_date DATE NOT NULL,
  actual_check_out DATE NULL,
  total_price DECIMAL(10,2) NOT NULL,
  guest_id INT NOT NULL,
  room_id INT NOT NULL,
  user_id INT NOT NULL,
  status ENUM('requested','active','completed','cancelled') NOT NULL DEFAULT 'requested',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_booking_guest FOREIGN KEY (guest_id) REFERENCES guests(id_guest),
  CONSTRAINT fk_booking_room FOREIGN KEY (room_id) REFERENCES rooms(id_room),
  CONSTRAINT fk_booking_user FOREIGN KEY (user_id) REFERENCES users(id_user)
) ENGINE=InnoDB;

INSERT INTO users(username,password_hash,role,full_name) VALUES
('admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin','Демо Администратор'),
('manager','866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5','manager','Демо Менеджер'),
('guest','6b93ccba414ac1d0ae1e77f3fac560c748a6701ed6946735a49d463351518e16','guest','Демо Гость')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name),role=VALUES(role);

-- Категории, номера и цены используются исключительно для демонстрации.
INSERT INTO rooms(room_number,category,capacity,price,status) VALUES
('MOST-01','Single',1,4230,'free'),
('MOST-02','Double',2,5130,'free'),
('MOST-03','Double',2,5130,'free'),
('MOST-04','Comfort',3,6200,'free'),
('MOST-05','Семейный',3,6800,'free'),
('MOST-06','Семейный',3,6800,'free'),
('MOST-07','Улучшенный двухместный стандарт',2,5700,'free'),
('MOST-08','Улучшенный двухместный стандарт',2,5700,'free')
ON DUPLICATE KEY UPDATE category=VALUES(category),capacity=VALUES(capacity),price=VALUES(price);
