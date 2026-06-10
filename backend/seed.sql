CREATE TABLE IF NOT EXISTS Registration_Requests (
    RequestID      INT PRIMARY KEY AUTO_INCREMENT,
    First_Name     VARCHAR(50) NOT NULL,
    Last_Name      VARCHAR(50) NOT NULL,
    Email          VARCHAR(100) NOT NULL,
    Account_Type   ENUM('Student', 'Staff') NOT NULL,
    DoB            DATE,
    Department     VARCHAR(100),
    Contact_Number VARCHAR(20),
    Address        TEXT,
    Father_Name    VARCHAR(100),
    Hostel_Name    VARCHAR(100),
    Room_Number    VARCHAR(20),
    Category       VARCHAR(30),
    Status         ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    Created_At     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO Users (UserID, First_Name, Last_Name, Email, Account_Type) VALUES
(1, 'Muhammad', 'Azaan', 'zainif63@gmail.com', 'Admin'),
(2, 'Muhammad', 'Azaan', 'mazaan.bscs25seecs@seecs.edu.pk', 'Student'),
(3, 'Jane', 'Smith', 'jane.student@seecs.edu.pk', 'Student'),
(4, 'Muhammad', 'Azaan', 'zainif630@gmail.com', 'Staff'),
(5, 'Bob', 'Jones', 'bob.student@seecs.edu.pk', 'Student'),
(6, 'Alice', 'Staff', 'alice.staff@seecs.edu.pk', 'Staff'),
(7, 'Charlie', 'Chef', 'charlie.chef@seecs.edu.pk', 'Staff');

INSERT IGNORE INTO Student (UserID, DoB, Department, Contact_Number, Address, Father_Name, Hostel_Name, Room_Number) VALUES
(2, '2004-05-15', 'CS', '0300-1234567', 'H-12 NUST', 'John Smith', 'Ghazali', '101'),
(3, '2003-11-20', 'SE', '0300-7654321', 'H-12 NUST', 'Mike Jones', 'Rumi', '202'),
(5, '2004-01-10', 'EE', '0321-9876543', 'H-12 NUST', 'David Jones', 'Attar', '303');

INSERT IGNORE INTO Staff_Category (Category, Working_hours, Salary) VALUES
('Chef', 8.0, 50000.00),
('Server', 6.0, 30000.00);

INSERT IGNORE INTO Staff (UserID, Category) VALUES
(4, 'Server'),
(6, 'Chef');

INSERT IGNORE INTO Ingredients (Name, Unit, Unit_cost, Total_Quantity) VALUES
('Basmati Rice', 'kg', 350.00, 500.00),
('Chicken', 'kg', 600.00, 200.00),
('Cooking Oil', 'Litre', 450.00, 100.00),
('Salt', 'kg', 50.00, 50.00),
('Lentils (Daal)', 'kg', 280.00, 150.00),
('Onion', 'kg', 150.00, 100.00),
('Tomato', 'kg', 100.00, 80.00),
('Garlic', 'kg', 400.00, 20.00),
('Ginger', 'kg', 350.00, 20.00),
('Flour', 'kg', 120.00, 1000.00);

INSERT IGNORE INTO Food_Items (Name, Quantity, Price) VALUES
('Chicken Biryani', 1.0, 250.00),
('Daal Mash', 1.0, 150.00),
('Special Tea', 1.0, 50.00),
('Aloo Paratha', 1.0, 80.00),
('Chicken Karahi', 1.0, 450.00),
('Mixed Vegetable', 1.0, 120.00),
('Roti', 1.0, 15.00);

INSERT IGNORE INTO Food_Item_Ingredients (Item_ID, Ingredient_ID, Ingredient_Quantity) VALUES
(1, 1, 0.5), (1, 2, 0.3), (1, 3, 0.1),
(2, 5, 0.4), (2, 3, 0.05),
(4, 10, 0.2), (4, 3, 0.01),
(5, 2, 0.5), (5, 3, 0.1), (5, 6, 0.1), (5, 7, 0.05),
(6, 6, 0.2), (6, 7, 0.1), (6, 3, 0.05),
(7, 10, 0.15);

INSERT IGNORE INTO Menu_Schedule (Date, meal_type, status) VALUES
(CURDATE(), 'Breakfast', 'Active'),
(CURDATE(), 'Lunch', 'Active'),
(CURDATE(), 'Dinner', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Breakfast', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Lunch', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Dinner', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Breakfast', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Lunch', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Dinner', 'Active');

INSERT IGNORE INTO Menu_Food_Items (Schedule_ID, Item_ID) VALUES
(1, 3), (2, 1), (3, 2),
(4, 4), (4, 3),
(5, 5), (5, 7),
(6, 6), (6, 7),
(7, 4), (7, 3),
(8, 1), (8, 7),
(9, 2), (9, 7);

INSERT IGNORE INTO Mess_Off (User_ID, Start_Date, End_Date, Status) VALUES
(2, DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Pending'),
(3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Approved');

INSERT IGNORE INTO Bills (User_ID, Amount, Due_Date, Month, Status) VALUES
(2, 4500.00, DATE_ADD(CURDATE(), INTERVAL 10 DAY), '2026-05-01', 'Unpaid'),
(3, 3800.00, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '2026-05-01', 'Overdue'),
(2, 4200.00, DATE_SUB(CURDATE(), INTERVAL 30 DAY), '2026-04-01', 'Paid');

INSERT IGNORE INTO Transactions (Billing_ID, Amount_Paid, Payment_Method, Transaction_Status) VALUES
(3, 4200.00, 'Online', 'Success');

INSERT IGNORE INTO Ratings (User_ID, Item_ID, Schedule_ID, Score) VALUES
(2, 1, 2, 5),
(3, 1, 2, 4),
(2, 3, 1, 3);

INSERT IGNORE INTO Votes (User_ID, Food_ID) VALUES
(2, 1),
(3, 5),
(2, 5);
