-- 1. Create and Use the Database
CREATE DATABASE IF NOT EXISTS mess_db;
USE mess_db;

-- 2. Create the Users Table
-- We use ENUM to restrict Account_Type to exactly what we finalized.
CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL, -- In production, this would be a hash
    Account_Type ENUM('Student', 'Staff', 'Admin') NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create a basic Food_Items table
-- This allows you to test the "Menu" features immediately.
CREATE TABLE IF NOT EXISTS Food_Items (
    FoodID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Is_Available BOOLEAN DEFAULT TRUE
);

-- 4. SEED DATA (Test Data)
-- Adding these ensures your "Check Mess Menu" button actually returns something.

INSERT INTO Users (First_Name, Last_Name, Email, Password, Account_Type)
VALUES
('Muhammad', 'Azaan', 'mazaan.bscs25seecs@seecs.edu.pk', 'admin123', 'Admin'),
('Bob', 'Khan', 'farhad@nust.edu.pk', 'student123', 'Student');

INSERT INTO Food_Items (Name, Description, Price)
VALUES
('Chicken Biryani', 'Spicy Sindhi style biryani with raita', 250.00),
('Daal Mash', 'Traditional butter-tempered lentils', 120.00),
('Aloo Palak', 'Fresh spinach with sautéed potatoes', 150.00);