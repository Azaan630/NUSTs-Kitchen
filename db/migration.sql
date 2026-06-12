-- Migration: Add Sex column + Student Details view
-- Run against the deployed Aiven database.

ALTER TABLE Users
    ADD COLUMN Sex ENUM('Male', 'Female') DEFAULT NULL
    AFTER Account_Type;

ALTER TABLE Registration_Requests
    ADD COLUMN Sex ENUM('Male', 'Female') DEFAULT NULL
    AFTER Account_Type;

ALTER TABLE Users
    ADD COLUMN Profile_Picture VARCHAR(500) DEFAULT NULL
    AFTER Sex;

ALTER TABLE Food_Items
    ADD COLUMN Image_Path VARCHAR(500) DEFAULT NULL
    AFTER Quantity;

ALTER TABLE Ingredients
    ADD COLUMN Image_Path VARCHAR(500) DEFAULT NULL
    AFTER Total_Quantity;

CREATE OR REPLACE VIEW vw_StaffDetails AS
SELECT
    s.UserID,
    u.First_Name,
    u.Last_Name,
    u.Email,
    u.Sex,
    u.Profile_Picture,
    s.Category,
    sc.Working_hours,
    sc.Salary
FROM Staff s
JOIN Users u ON s.UserID = u.UserID
JOIN Staff_Category sc ON s.Category = sc.Category;

CREATE OR REPLACE VIEW vw_StudentDetails AS
SELECT
    u.UserID,
    u.First_Name,
    u.Last_Name,
    u.Email,
    u.Sex,
    u.Profile_Picture,
    u.Account_Type,
    s.DoB,
    s.Department,
    s.Contact_Number,
    s.Address,
    s.Father_Name,
    s.Hostel_Name,
    s.Room_Number
FROM Users u
JOIN Student s ON u.UserID = s.UserID;
