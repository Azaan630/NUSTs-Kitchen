-- ============================================================================
-- COMPREHENSIVE SEED DATA for MySQL Workbench
-- Run this after schema exists (db/init.sql has been executed)
-- Contains: ALL data rows with image URLs, recipes, 7-day menu, bills, votes, ratings
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Transactions;
TRUNCATE TABLE Bills;
TRUNCATE TABLE Votes;
TRUNCATE TABLE Ratings;
TRUNCATE TABLE Mess_Off;
TRUNCATE TABLE Menu_Food_Items;
TRUNCATE TABLE Menu_Schedule;
TRUNCATE TABLE Food_Item_Ingredients;
TRUNCATE TABLE Food_Items;
TRUNCATE TABLE Ingredients;
TRUNCATE TABLE Staff_Contact_Numbers;
TRUNCATE TABLE Staff;
TRUNCATE TABLE Staff_Category;
TRUNCATE TABLE Student;
TRUNCATE TABLE Registration_Requests;
TRUNCATE TABLE Users;
TRUNCATE TABLE System_Config;

SET FOREIGN_KEY_CHECKS = 1;

-- Migration columns (safe to re-run)
ALTER TABLE Users ADD COLUMN IF NOT EXISTS Profile_Picture VARCHAR(500) DEFAULT NULL AFTER Sex;
ALTER TABLE Food_Items ADD COLUMN IF NOT EXISTS Image_Path VARCHAR(500) DEFAULT NULL AFTER Quantity;
ALTER TABLE Ingredients ADD COLUMN IF NOT EXISTS Image_Path VARCHAR(500) DEFAULT NULL AFTER Total_Quantity;
ALTER TABLE Registration_Requests ADD COLUMN IF NOT EXISTS Profile_Picture VARCHAR(500) DEFAULT NULL AFTER Category;

-- ============================================================================
-- USERS (10)
-- ============================================================================
INSERT INTO Users (UserID, First_Name, Last_Name, Email, Account_Type, Sex, Profile_Picture) VALUES
(1,  'Muhammad','Azaan',  'zainif63@gmail.com',              'Admin',   'Male',   'https://picsum.photos/seed/admin1/200/200'),
(2,  'Muhammad','Azaan',  'mazaan.bscs25seecs@seecs.edu.pk', 'Student', 'Male',   'https://picsum.photos/seed/student1/200/200'),
(3,  'Muhammad','Azaan',  'zainif630@gmail.com',             'Staff',   'Male',   'https://picsum.photos/seed/staff1/200/200'),
(4,  'Aisha',   'Khan',   'aisha.student@seecs.edu.pk',      'Student', 'Female', 'https://picsum.photos/seed/aisha/200/200'),
(5,  'Bilal',   'Ahmed',  'bilal.student@seecs.edu.pk',      'Student', 'Male',   'https://picsum.photos/seed/bilal/200/200'),
(6,  'Fatima',  'Ali',    'fatima.staff@seecs.edu.pk',       'Staff',   'Female', 'https://picsum.photos/seed/fatima/200/200'),
(7,  'Zara',    'Malik',  'zara.student@seecs.edu.pk',       'Student', 'Female', 'https://picsum.photos/seed/zara/200/200'),
(8,  'Hassan',  'Raza',   'hassan.student@seecs.edu.pk',     'Student', 'Male',   'https://picsum.photos/seed/hassan/200/200'),
(9,  'Sara',    'Javed',  'sara.student@seecs.edu.pk',       'Student', 'Female', 'https://picsum.photos/seed/sara/200/200'),
(10, 'Omar',    'Sheikh', 'omar.staff@seecs.edu.pk',          'Staff',   'Male',   'https://picsum.photos/seed/omar/200/200');

-- ============================================================================
-- STUDENTS
-- ============================================================================
INSERT INTO Student (UserID, DoB, Department, Contact_Number, Address, Father_Name, Hostel_Name, Room_Number) VALUES
(2,  '2004-05-15','Computer Science',       '0300-1234567','H-12 NUST Islamabad','John Azaan', 'Ghazali','101'),
(4,  '2003-08-22','Software Engineering',    '0300-2345678','H-12 NUST Islamabad','Imran Khan', 'Rumi',   '205'),
(5,  '2004-01-10','Electrical Engineering',  '0300-3456789','H-12 NUST Islamabad','Ahmed Bilal','Attar',  '310'),
(7,  '2005-03-14','Mechanical Engineering',  '0300-4567890','H-12 NUST Islamabad','Tariq Malik','Ghazali','115'),
(8,  '2003-11-30','Computer Science',        '0300-5678901','H-12 NUST Islamabad','Raza Shah',  'Rumi',   '220'),
(9,  '2004-07-05','Biotechnology',           '0300-6789012','H-12 NUST Islamabad','Javed Iqbal','Attar',  '405'),
(11, '2005-02-18','Civil Engineering',       '0300-7890123','H-12 NUST Islamabad','Usman Dar',  'Iqbal',  '118');

-- ============================================================================
-- STAFF CATEGORIES
-- ============================================================================
INSERT INTO Staff_Category (Category, Working_hours, Salary) VALUES
('Head Chef', 9.0, 85000.00),
('Chef',      8.0, 50000.00),
('Server',    6.0, 30000.00),
('Cleaner',   8.0, 28000.00);

-- ============================================================================
-- STAFF
-- ============================================================================
INSERT INTO Staff (UserID, Category) VALUES
(3,  'Server'),
(6,  'Head Chef'),
(10, 'Chef');

-- ============================================================================
-- STAFF CONTACT NUMBERS
-- ============================================================================
INSERT INTO Staff_Contact_Numbers (UserID, Contact_Number) VALUES
(3,  '0300-1112233'),
(3,  '051-8315271'),
(6,  '0300-4445566'),
(10, '0300-7778899');

-- ============================================================================
-- INGREDIENTS (20, with picsum images)
-- ============================================================================
INSERT INTO Ingredients (Ingredient_ID, Name, Unit, Unit_cost, Total_Quantity, Image_Path) VALUES
(1,  'Basmati Rice',     'kg',    350.00, 500.000,'https://picsum.photos/seed/rice/400/300'),
(2,  'Chicken Breast',   'kg',    600.00, 200.000,'https://picsum.photos/seed/chicken/400/300'),
(3,  'Cooking Oil',      'Litre', 450.00, 100.000,'https://picsum.photos/seed/oil/400/300'),
(4,  'Salt',             'kg',    50.00,  50.000,'https://picsum.photos/seed/salt/400/300'),
(5,  'Lentils (Daal)',   'kg',    280.00, 150.000,'https://picsum.photos/seed/daal/400/300'),
(6,  'Onion',            'kg',    150.00, 100.000,'https://picsum.photos/seed/onion/400/300'),
(7,  'Tomato',           'kg',    100.00,  80.000,'https://picsum.photos/seed/tomato/400/300'),
(8,  'Garlic',           'kg',    400.00,  20.000,'https://picsum.photos/seed/garlic/400/300'),
(9,  'Ginger',           'kg',    350.00,  20.000,'https://picsum.photos/seed/ginger/400/300'),
(10, 'Wheat Flour',      'kg',    120.00,1000.000,'https://picsum.photos/seed/flour/400/300'),
(11, 'Butter',           'kg',    800.00,  30.000,'https://picsum.photos/seed/butter/400/300'),
(12, 'Yogurt',           'kg',    200.00,  60.000,'https://picsum.photos/seed/yogurt/400/300'),
(13, 'Red Chili Powder', 'kg',    450.00,  15.000,'https://picsum.photos/seed/chili/400/300'),
(14, 'Turmeric Powder',  'kg',    350.00,  12.000,'https://picsum.photos/seed/turmeric/400/300'),
(15, 'Cumin Seeds',      'kg',    600.00,  10.000,'https://picsum.photos/seed/cumin/400/300'),
(16, 'Milk',             'Litre', 180.00,  80.000,'https://picsum.photos/seed/milk/400/300'),
(17, 'Eggs',             'dozen', 240.00,  50.000,'https://picsum.photos/seed/eggs/400/300'),
(18, 'Potato',           'kg',    80.00,  200.000,'https://picsum.photos/seed/potato/400/300'),
(19, 'Green Chili',      'kg',    200.00,  15.000,'https://picsum.photos/seed/greenchili/400/300'),
(20, 'Coriander Leaves', 'bunch', 30.00,   50.000,'https://picsum.photos/seed/coriander/400/300');

-- ============================================================================
-- FOOD ITEMS (15, with images & ratings)
-- ============================================================================
INSERT INTO Food_Items (Item_ID, Name, Quantity, Image_Path, Ratings_Average, Vote_Count, Price) VALUES
(1,  'Chicken Biryani',  1.0,'https://picsum.photos/seed/biryani/400/300', 4.5,12,250.00),
(2,  'Daal Mash',        1.0,'https://picsum.photos/seed/daalmash/400/300',3.8,8, 150.00),
(3,  'Special Tea',      1.0,'https://picsum.photos/seed/tea/400/300',     4.2,15,50.00),
(4,  'Aloo Paratha',     1.0,'https://picsum.photos/seed/paratha/400/300', 4.0,9, 80.00),
(5,  'Chicken Karahi',   1.0,'https://picsum.photos/seed/karahi/400/300',  4.7,20,450.00),
(6,  'Mixed Vegetable',  1.0,'https://picsum.photos/seed/veg/400/300',     3.5,5, 120.00),
(7,  'Roti',             1.0,'https://picsum.photos/seed/roti/400/300',    4.1,3, 15.00),
(8,  'Nihari',           1.0,'https://picsum.photos/seed/nihari/400/300',  4.8,25,380.00),
(9,  'Chicken Pulao',    1.0,'https://picsum.photos/seed/pulao/400/300',   4.3,10,200.00),
(10, 'Omelette',         1.0,'https://picsum.photos/seed/omelette/400/300',3.9,7, 60.00),
(11, 'Haleem',           1.0,'https://picsum.photos/seed/haleem/400/300',  4.6,18,300.00),
(12, 'Chicken Tikka',    1.0,'https://picsum.photos/seed/tikka/400/300',   4.4,14,350.00),
(13, 'Fruit Chaat',      1.0,'https://picsum.photos/seed/chaat/400/300',   4.0,6, 70.00),
(14, 'Keema Naan',       1.0,'https://picsum.photos/seed/keema/400/300',   4.2,11,120.00),
(15, 'Gulab Jamun',      1.0,'https://picsum.photos/seed/gulab/400/300',   4.9,22,50.00);

-- ============================================================================
-- RECIPES (Food_Item_Ingredients) — every item gets ingredients
-- ============================================================================
INSERT INTO Food_Item_Ingredients (Item_ID, Ingredient_ID, Ingredient_Quantity) VALUES
(1,1,0.50),(1,2,0.30),(1,3,0.10),(1,6,0.15),(1,7,0.10),(1,12,0.10),(1,13,0.01),(1,4,0.01),
(2,5,0.40),(2,3,0.05),(2,6,0.10),(2,8,0.02),(2,15,0.01),
(3,16,0.20),(3,9,0.01),
(4,10,0.20),(4,18,0.15),(4,11,0.03),(4,6,0.05),(4,19,0.01),
(5,2,0.50),(5,3,0.10),(5,7,0.20),(5,6,0.10),(5,9,0.02),(5,8,0.02),(5,13,0.01),(5,12,0.10),(5,20,0.01),
(6,6,0.15),(6,7,0.10),(6,18,0.20),(6,3,0.05),(6,14,0.01),
(7,10,0.15),(7,3,0.005),(7,4,0.002),
(8,2,0.40),(8,3,0.10),(8,6,0.10),(8,9,0.02),(8,8,0.02),(8,13,0.01),(8,14,0.01),(8,15,0.01),(8,10,0.05),
(9,1,0.40),(9,2,0.25),(9,3,0.08),(9,6,0.10),(9,12,0.08),(9,15,0.01),(9,4,0.01),
(10,17,0.13),(10,6,0.05),(10,3,0.01),(10,19,0.01),(10,4,0.002),
(11,5,0.30),(11,2,0.20),(11,3,0.08),(11,10,0.10),(11,6,0.10),(11,9,0.01),(11,8,0.02),(11,13,0.008),(11,14,0.005),(11,15,0.005),(11,20,0.005),
(12,2,0.40),(12,12,0.15),(12,3,0.05),(12,13,0.01),(12,14,0.005),(12,15,0.005),(12,9,0.01),(12,8,0.01),
(13,18,0.10),(13,12,0.05),(13,4,0.002),
(14,10,0.25),(14,2,0.30),(14,6,0.08),(14,11,0.04),(14,9,0.01),(14,8,0.01),(14,13,0.005),(14,12,0.05),
(15,16,0.15),(15,10,0.05),(15,11,0.03),(15,3,0.05);

-- ============================================================================
-- MENU SCHEDULE (7 days x 3 meals)
-- ============================================================================
INSERT INTO Menu_Schedule (Date, meal_type, status) VALUES
(CURDATE(),                               'Breakfast','Active'),
(CURDATE(),                               'Lunch',    'Active'),
(CURDATE(),                               'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 1 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 1 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 1 DAY),     'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 2 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 2 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 2 DAY),     'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 3 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 3 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 3 DAY),     'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 4 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 4 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 4 DAY),     'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 5 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 5 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 5 DAY),     'Dinner',   'Active'),
(DATE_ADD(CURDATE(),INTERVAL 6 DAY),     'Breakfast','Active'),
(DATE_ADD(CURDATE(),INTERVAL 6 DAY),     'Lunch',    'Active'),
(DATE_ADD(CURDATE(),INTERVAL 6 DAY),     'Dinner',   'Active');

-- ============================================================================
-- MENU FOOD ITEMS
-- ============================================================================
INSERT INTO Menu_Food_Items (Schedule_ID, Item_ID) VALUES
(1,3),(1,10),(1,4),
(2,1),(2,5),(2,7),
(3,2),(3,6),(3,7),
(4,4),(4,3),(4,10),
(5,9),(5,12),(5,7),
(6,8),(6,14),(6,7),
(7,10),(7,4),(7,3),
(8,1),(8,6),
(9,2),(9,14),
(10,3),(10,10),(10,13),
(11,5),(11,7),
(12,11),(12,7),
(13,4),(13,3),
(14,8),(14,7),
(15,9),(15,6),(15,7),
(16,10),(16,4),(16,15),
(17,12),(17,1),
(18,2),(18,7),(18,15),
(19,13),(19,3),
(20,5),(20,9),(20,7),
(21,11),(21,14),(21,7);

-- ============================================================================
-- MESS OFF REQUESTS
-- ============================================================================
INSERT INTO Mess_Off (User_ID, Start_Date, End_Date, Status) VALUES
(2,DATE_ADD(CURDATE(),INTERVAL 5 DAY),  DATE_ADD(CURDATE(),INTERVAL 10 DAY), 'Pending'),
(4,DATE_ADD(CURDATE(),INTERVAL 1 DAY),  DATE_ADD(CURDATE(),INTERVAL 3 DAY),  'Approved'),
(5,DATE_ADD(CURDATE(),INTERVAL 8 DAY),  DATE_ADD(CURDATE(),INTERVAL 12 DAY), 'Pending'),
(7,DATE_ADD(CURDATE(),INTERVAL 2 DAY),  DATE_ADD(CURDATE(),INTERVAL 4 DAY),  'Pending'),
(8,DATE_SUB(CURDATE(),INTERVAL 2 DAY),  DATE_ADD(CURDATE(),INTERVAL 1 DAY),  'Approved'),
(9,DATE_ADD(CURDATE(),INTERVAL 10 DAY), DATE_ADD(CURDATE(),INTERVAL 14 DAY), 'Pending'),
(2,DATE_SUB(CURDATE(),INTERVAL 5 DAY),  DATE_SUB(CURDATE(),INTERVAL 2 DAY),  'Rejected'),
(11,DATE_ADD(CURDATE(),INTERVAL 3 DAY), DATE_ADD(CURDATE(),INTERVAL 6 DAY),  'Approved');

-- ============================================================================
-- BILLS (multiple per student: paid, unpaid, overdue)
-- ============================================================================
INSERT INTO Bills (User_ID, Amount, Due_Date, Month, Status) VALUES
(2, 4500.00,DATE_ADD(CURDATE(),INTERVAL 10 DAY), '2026-05-01','Unpaid'),
(2, 4200.00,DATE_SUB(CURDATE(),INTERVAL 30 DAY),'2026-04-01','Paid'),
(2, 4600.00,DATE_ADD(CURDATE(),INTERVAL 25 DAY), '2026-06-01','Unpaid'),
(4, 3800.00,DATE_SUB(CURDATE(),INTERVAL 2 DAY),  '2026-05-01','Overdue'),
(4, 4000.00,DATE_SUB(CURDATE(),INTERVAL 40 DAY), '2026-04-01','Paid'),
(5, 4500.00,DATE_ADD(CURDATE(),INTERVAL 10 DAY), '2026-05-01','Unpaid'),
(5, 4300.00,DATE_SUB(CURDATE(),INTERVAL 5 DAY),  '2026-04-01','Overdue'),
(7, 4000.00,DATE_ADD(CURDATE(),INTERVAL 15 DAY), '2026-05-01','Unpaid'),
(7, 3900.00,DATE_SUB(CURDATE(),INTERVAL 35 DAY), '2026-03-01','Paid'),
(8, 5000.00,DATE_ADD(CURDATE(),INTERVAL 8 DAY),  '2026-05-01','Unpaid'),
(8, 4800.00,DATE_SUB(CURDATE(),INTERVAL 3 DAY),  '2026-04-01','Overdue'),
(9, 4100.00,DATE_ADD(CURDATE(),INTERVAL 12 DAY), '2026-05-01','Paid'),
(9, 4200.00,DATE_ADD(CURDATE(),INTERVAL 28 DAY), '2026-06-01','Unpaid'),
(11,4400.00,DATE_ADD(CURDATE(),INTERVAL 20 DAY), '2026-05-01','Paid'),
(11,4500.00,DATE_SUB(CURDATE(),INTERVAL 1 DAY),  '2026-04-01','Overdue');

-- ============================================================================
-- TRANSACTIONS
-- ============================================================================
INSERT INTO Transactions (Billing_ID, Amount_Paid, Payment_Method, Transaction_Status) VALUES
(2, 4200.00,'Online','Success'),
(5, 4000.00,'Cash',  'Success'),
(9, 3900.00,'Card',  'Success'),
(12,4100.00,'Online','Success'),
(14,4400.00,'Online','Success'),
(1, 2000.00,'Cash',  'Success'),
(1, 1500.00,'Online','Success');

-- ============================================================================
-- RATINGS
-- ============================================================================
INSERT INTO Ratings (User_ID, Item_ID, Schedule_ID, Score) VALUES
(2,1,2,5),(2,3,1,3),(2,5,2,5),(2,7,2,4),
(4,1,2,4),(4,9,5,5),(4,6,3,2),
(5,8,6,5),(5,12,5,4),(5,4,4,3),
(7,10,1,4),(7,13,10,5),(7,15,16,5),
(8,5,2,5),(8,2,3,3),(8,11,12,4),
(9,3,1,4),(9,1,2,5),(9,14,6,4);

-- ============================================================================
-- VOTES
-- ============================================================================
INSERT INTO Votes (User_ID, Food_ID) VALUES
(2,1),(2,5),(2,8),
(4,5),(4,12),(4,15),
(5,1),(5,9),(5,14),
(7,10),(7,13),(7,15),
(8,8),(8,11),(8,12),
(9,3),(9,5),(9,15),
(11,1),(11,8);

-- ============================================================================
-- REGISTRATION REQUESTS
-- ============================================================================
INSERT INTO Registration_Requests (First_Name,Last_Name,Email,Account_Type,Sex,DoB,Department,Contact_Number,Address,Father_Name,Hostel_Name,Room_Number,Category,Status,Profile_Picture) VALUES
('Usman', 'Dar',    'usman.dar@seecs.edu.pk',    'Student','Male',  '2005-02-18','Civil Engineering',      '0300-7890123','H-12 NUST','Mr. Dar',   'Iqbal',  '118',NULL,   'Pending','https://picsum.photos/seed/usman/200/200'),
('Nadia', 'Hussain','nadia.hussain@seecs.edu.pk', 'Student','Female','2004-09-12','Business Administration','0300-8901234','H-12 NUST','Mr. Hussain','Ghazali','210',NULL,   'Pending','https://picsum.photos/seed/nadia/200/200'),
('Kamran','Tariq',  'kamran.tariq@gmail.com',     'Staff',  'Male',  '1990-03-05',NULL,                     '0300-9012345','H-12 NUST','Mr. Tariq',  NULL,     NULL, 'Server','Pending','https://picsum.photos/seed/kamran/200/200');

-- ============================================================================
-- SYSTEM CONFIG
-- ============================================================================
INSERT INTO System_Config (Config_Key, Value) VALUES
('daily_mess_rate', '150.00'),
('maintenance_mode','false'),
('system_version',  '2.0.0')
ON DUPLICATE KEY UPDATE Value=VALUES(Value);
