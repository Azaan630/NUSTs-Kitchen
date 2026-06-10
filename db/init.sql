CREATE TABLE IF NOT EXISTS Users (
    UserID      INT PRIMARY KEY AUTO_INCREMENT,
    First_Name  VARCHAR(50) NOT NULL,
    Last_Name   VARCHAR(50) NOT NULL,
    Email       VARCHAR(100) UNIQUE NOT NULL,
    Account_Type ENUM('Student', 'Staff', 'Admin') NOT NULL
);

CREATE TABLE IF NOT EXISTS Student (
    UserID          INT PRIMARY KEY,
    DoB             DATE NOT NULL,
    Department      VARCHAR(100) NOT NULL,
    Contact_Number  VARCHAR(20),
    Address         TEXT,
    Father_Name     VARCHAR(100),
    Hostel_Name     VARCHAR(100),
    Room_Number     VARCHAR(20),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Staff_Category (
    Category          VARCHAR(30) PRIMARY KEY,
    Working_hours     DECIMAL(4,1) NOT NULL,
    Salary            DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Staff (
    UserID            INT PRIMARY KEY,
    Category          VARCHAR(30) NOT NULL,
    CONSTRAINT FK_Staff_User      FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT FK_Staff_Category  FOREIGN KEY (Category) REFERENCES Staff_Category(Category) ON DELETE RESTRICT ON UPDATE CASCADE
);

# Multivalued attribute: separate table
CREATE TABLE IF NOT EXISTS Staff_Contact_Numbers (
    Contact_ID      INT PRIMARY KEY AUTO_INCREMENT,
    UserID          INT NOT NULL,
    Contact_Number  VARCHAR(20) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Staff(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Ingredients (
    Ingredient_ID   INT PRIMARY KEY AUTO_INCREMENT,
    Name            VARCHAR(100) NOT NULL,
    Unit            VARCHAR(100) NOT NULL,
    Unit_cost       DECIMAL(10,2) NOT NULL,
    Total_Quantity  DECIMAL(10,3) NOT NULL DEFAULT 0.000
);

CREATE TABLE IF NOT EXISTS Food_Items (
    Item_ID             INT PRIMARY KEY AUTO_INCREMENT,
    Name                VARCHAR(100) NOT NULL,
    Quantity            DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    Ratings_Average     DECIMAL(3,2) DEFAULT NULL COMMENT 'Average rating (1-5), NULL if no ratings',
    Vote_Count          INT DEFAULT 0,
    Price               DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS Food_Item_Ingredients (
    Item_ID         INT NOT NULL,
    Ingredient_ID   INT NOT NULL,
    Ingredient_Quantity DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (Item_ID, Ingredient_ID),
    FOREIGN KEY (Item_ID)       REFERENCES Food_Items(Item_ID)      ON DELETE CASCADE,
    FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Menu_Schedule (
    Schedule_ID INT PRIMARY KEY AUTO_INCREMENT,
    Date        DATE NOT NULL,
    meal_type   ENUM('Breakfast','Lunch','Dinner') NOT NULL,
    status      ENUM('Active','Cancelled') NOT NULL DEFAULT 'Active',
    CONSTRAINT UQ_Slot UNIQUE (Date, meal_type)
);

CREATE TABLE IF NOT EXISTS Menu_Food_Items (
    Schedule_ID INT NOT NULL,
    Item_ID     INT NOT NULL,
    PRIMARY KEY (Schedule_ID, Item_ID),
    FOREIGN KEY (Schedule_ID) REFERENCES Menu_Schedule(Schedule_ID) ON DELETE CASCADE,
    FOREIGN KEY (Item_ID)     REFERENCES Food_Items(Item_ID)        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Mess_Off (
    Mess_Off_ID     INT PRIMARY KEY AUTO_INCREMENT,
    User_ID         INT NOT NULL,
    Start_Date      DATE NOT NULL,
    End_Date        DATE NOT NULL,
    Request_Date    DATE NOT NULL DEFAULT (CURRENT_DATE),
    Status          ENUM('Pending', 'Approved', 'Rejected', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE,
    CONSTRAINT CHK_Date_Range CHECK (End_Date >= Start_Date),
    CONSTRAINT UQ_Request UNIQUE (User_ID, Start_Date, End_Date)
);

CREATE TABLE IF NOT EXISTS Ratings (
    Rating_ID   INT PRIMARY KEY AUTO_INCREMENT,
    User_ID     INT NOT NULL,
    Item_ID     INT NOT NULL,
    Schedule_ID INT NOT NULL,
    Score       TINYINT NOT NULL CHECK (Score BETWEEN 1 AND 5),
    Rated_At    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE,
    FOREIGN KEY (Item_ID) REFERENCES Food_Items(Item_ID) ON DELETE CASCADE,
    FOREIGN KEY (Schedule_ID) REFERENCES Menu_Schedule(Schedule_ID) ON DELETE CASCADE,
    CONSTRAINT UQ_Rating UNIQUE (User_ID, Item_ID, Schedule_ID)
);

CREATE TABLE IF NOT EXISTS Votes (
    Vote_ID     INT PRIMARY KEY AUTO_INCREMENT,
    User_ID     INT NOT NULL,
    Food_ID     INT NOT NULL,
    Date_Time   DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (User_ID, Food_ID),
    FOREIGN KEY (User_ID) REFERENCES Student(UserID)    ON DELETE CASCADE,
    FOREIGN KEY (Food_ID) REFERENCES Food_Items(Item_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Bills (
    Billing_ID      INT PRIMARY KEY AUTO_INCREMENT,
    User_ID         INT NOT NULL,
    Issue_Date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    Amount          DECIMAL(10,2) NOT NULL CHECK (Amount >= 0),
    Due_Date        DATE NOT NULL,
    Month           DATE NOT NULL COMMENT 'First day of the billing month',
    Status          ENUM('Paid', 'Unpaid', 'Overdue') DEFAULT 'Unpaid',
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Transactions (
    Billing_ID          INT NOT NULL,           # FK from owner entity Bills
    Transaction_ID      INT AUTO_INCREMENT,     # Partial key
    Amount_Paid         DECIMAL(10,2) NOT NULL CHECK (Amount_Paid > 0),
    Payment_Date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Payment_Method      ENUM('Cash','Card','Online') NOT NULL,
    Transaction_Status  ENUM('Success', 'Failed', 'Pending') NOT NULL,
    PRIMARY KEY (Billing_ID, Transaction_ID),   # Composite PK
    KEY (Transaction_ID),                       # the "must be defined as a key" rule
    FOREIGN KEY (Billing_ID) REFERENCES Bills(Billing_ID) ON DELETE CASCADE
);

# SYSTEM CONFIGURATION
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

CREATE TABLE IF NOT EXISTS System_Config (
    Config_Key        VARCHAR(50) PRIMARY KEY,
    Value             VARCHAR(100) NOT NULL
);

INSERT INTO System_Config VALUES ('daily_mess_rate', '150.00')
ON DUPLICATE KEY UPDATE Value=Value;

# --- VIEWS ---

CREATE OR REPLACE VIEW vw_MonthlyBillingSummary AS
SELECT
    b.User_ID,
    DATE_FORMAT(b.Month, '%Y-%m') AS Billing_Month,
    COUNT(b.Billing_ID) AS Total_Bills,
    SUM(b.Amount) AS Total_Amount,
    SUM(IFNULL(t.Total_Paid, 0)) AS Total_Collected,
    SUM(b.Amount) - SUM(IFNULL(t.Total_Paid, 0)) AS Outstanding
FROM Bills b
LEFT JOIN (
    SELECT Billing_ID, SUM(Amount_Paid) AS Total_Paid
    FROM Transactions
    WHERE Transaction_Status = 'Success'
    GROUP BY Billing_ID
) t ON b.Billing_ID = t.Billing_ID
GROUP BY b.User_ID, DATE_FORMAT(b.Month, '%Y-%m');

CREATE OR REPLACE VIEW vw_MessOffSummary AS
SELECT
    User_ID,
    DATE_FORMAT(Start_Date, '%Y-%m') AS Month,
    SUM(DATEDIFF(LEAST(End_Date, LAST_DAY(Start_Date)), GREATEST(Start_Date, DATE_FORMAT(Start_Date, '%Y-%m-01'))) + 1) AS Approved_Days
FROM Mess_Off
WHERE Status = 'Approved'
GROUP BY User_ID, Month;

CREATE OR REPLACE VIEW vw_MenuSchedule AS
SELECT
    ms.Schedule_ID,
    ms.Date AS Date,
    ms.meal_type AS meal_type,
    ms.status AS Slot_Status,
    fi.Item_ID,
    fi.Name AS Food_Item_Name
FROM Menu_Schedule ms
LEFT JOIN Menu_Food_Items s ON ms.Schedule_ID = s.Schedule_ID
LEFT JOIN Food_Items fi ON s.Item_ID = fi.Item_ID;

CREATE OR REPLACE VIEW vw_FoodItemCost AS
SELECT
    fi.Item_ID,
    fi.Name,
    SUM(i.Unit_cost * fgi.Ingredient_Quantity) AS Estimated_Cost
FROM Food_Items fi
JOIN Food_Item_Ingredients fgi ON fi.Item_ID = fgi.Item_ID
JOIN Ingredients i ON fgi.Ingredient_ID = i.Ingredient_ID
GROUP BY fi.Item_ID, fi.Name;

CREATE OR REPLACE VIEW vw_StaffDetails AS
SELECT
    s.UserID,
    u.First_Name,
    u.Last_Name,
    s.Category,
    sc.Working_hours,
    sc.Salary
FROM Staff s
JOIN Users u ON s.UserID = u.UserID
JOIN Staff_Category sc ON s.Category = sc.Category;

# --- STORED PROCEDURES ---

DELIMITER $$

CREATE PROCEDURE sp_GenerateMonthlyBills(IN p_month DATE)
BEGIN
    DECLARE v_daily_rate DECIMAL(10,2);
    DECLARE v_month_start DATE;
    DECLARE v_month_end DATE;
    DECLARE v_total_days INT;
    DECLARE v_student_id INT;
    DECLARE v_off_days INT;
    DECLARE v_due_date DATE;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE no_more_rows BOOLEAN DEFAULT FALSE;
    DECLARE cur_students CURSOR FOR SELECT UserID FROM Student;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_more_rows = TRUE;

    SELECT CAST(`Value` AS DECIMAL(10,2)) INTO v_daily_rate
    FROM System_Config WHERE Config_Key = 'daily_mess_rate';

    SET v_month_start = DATE_FORMAT(p_month, '%Y-%m-01');
    SET v_month_end   = LAST_DAY(v_month_start);
    SET v_total_days  = DAY(v_month_end);
    SET v_due_date    = DATE_ADD(v_month_start, INTERVAL 7 DAY);

    OPEN cur_students;
    student_loop: LOOP
        FETCH cur_students INTO v_student_id;
        IF no_more_rows THEN
            LEAVE student_loop;
        END IF;

        SELECT IFNULL(SUM(DATEDIFF(
            LEAST(End_Date, v_month_end),
            GREATEST(Start_Date, v_month_start)
        ) + 1), 0) INTO v_off_days
        FROM Mess_Off
        WHERE User_ID = v_student_id
          AND Status = 'Approved'
          AND Start_Date <= v_month_end
          AND End_Date >= v_month_start;

        SET v_amount = v_daily_rate * (v_total_days - v_off_days);

        IF v_amount > 0 THEN
            INSERT INTO Bills (Issue_Date, Amount, Due_Date, Month, Status, User_ID)
            VALUES (CURDATE(), v_amount, v_due_date, v_month_start, 'Unpaid', v_student_id);
        END IF;
    END LOOP student_loop;
    CLOSE cur_students;
END$$

CREATE PROCEDURE sp_RecordPayment(
    IN p_billing_id INT,
    IN p_amount DECIMAL(10,2),
    IN p_method ENUM('Cash','Card','Online')
)
BEGIN
    DECLARE v_total_paid DECIMAL(10,2);
    DECLARE v_bill_amount DECIMAL(10,2);

    INSERT INTO Transactions (Billing_ID, Amount_Paid, Payment_Method, Transaction_Status)
    VALUES (p_billing_id, p_amount, p_method, 'Success');

    SELECT SUM(Amount_Paid) INTO v_total_paid
    FROM Transactions
    WHERE Billing_ID = p_billing_id AND Transaction_Status = 'Success';

    SELECT Amount INTO v_bill_amount FROM Bills WHERE Billing_ID = p_billing_id;

    IF v_total_paid >= v_bill_amount THEN
        UPDATE Bills SET Status = 'Paid' WHERE Billing_ID = p_billing_id;
    END IF;
END$$

CREATE PROCEDURE sp_ApproveMessOff(IN p_mess_off_id INT)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_start DATE;
    DECLARE v_end DATE;
    DECLARE v_count INT;

    SELECT User_ID, Start_Date, End_Date INTO v_user_id, v_start, v_end
    FROM Mess_Off WHERE Mess_Off_ID = p_mess_off_id AND Status = 'Pending';

    IF v_user_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pending request not found';
    END IF;

    SELECT IFNULL(SUM(DATEDIFF(LEAST(End_Date, LAST_DAY(v_start)),
                              GREATEST(Start_Date, DATE_FORMAT(v_start, '%Y-%m-01'))) + 1), 0)
    INTO v_count
    FROM Mess_Off
    WHERE User_ID = v_user_id
      AND Status = 'Approved'
      AND Mess_Off_ID <> p_mess_off_id
      AND Start_Date <= LAST_DAY(v_start)
      AND End_Date >= DATE_FORMAT(v_start, '%Y-%m-01');

    SET v_count = v_count + DATEDIFF(v_end, v_start) + 1;

    IF v_count > 12 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exceeds maximum 12 mess-off days per month';
    ELSE
        UPDATE Mess_Off SET Status = 'Approved' WHERE Mess_Off_ID = p_mess_off_id;
    END IF;
END$$

CREATE PROCEDURE sp_AddVote(IN p_user_id INT, IN p_food_id INT)
BEGIN
    INSERT INTO Votes (User_ID, Food_ID) VALUES (p_user_id, p_food_id);
    UPDATE Food_Items SET Vote_Count = Vote_Count + 1 WHERE Item_ID = p_food_id;
END$$

CREATE PROCEDURE sp_UpdateOverdueBills()
BEGIN
    UPDATE Bills
    SET Status = 'Overdue'
    WHERE Status = 'Unpaid' AND Due_Date < CURDATE();
END$$

DELIMITER ;

# --- TRIGGERS ---

DELIMITER $$

CREATE TRIGGER trg_update_avg_rating_insert AFTER INSERT ON Ratings
FOR EACH ROW
BEGIN
    UPDATE Food_Items
    SET Ratings_Average = (SELECT AVG(Score) FROM Ratings WHERE Item_ID = NEW.Item_ID)
    WHERE Item_ID = NEW.Item_ID;
END$$

CREATE TRIGGER trg_update_avg_rating_update AFTER UPDATE ON Ratings
FOR EACH ROW
BEGIN
    UPDATE Food_Items
    SET Ratings_Average = (SELECT AVG(Score) FROM Ratings WHERE Item_ID = NEW.Item_ID)
    WHERE Item_ID = NEW.Item_ID;
    IF OLD.Item_ID <> NEW.Item_ID THEN
        UPDATE Food_Items
        SET Ratings_Average = (SELECT AVG(Score) FROM Ratings WHERE Item_ID = OLD.Item_ID)
        WHERE Item_ID = OLD.Item_ID;
    END IF;
END$$

CREATE TRIGGER trg_update_avg_rating_delete AFTER DELETE ON Ratings
FOR EACH ROW
BEGIN
    UPDATE Food_Items
    SET Ratings_Average = (SELECT AVG(Score) FROM Ratings WHERE Item_ID = OLD.Item_ID)
    WHERE Item_ID = OLD.Item_ID;
END$$

CREATE TRIGGER trg_deduct_vote AFTER DELETE ON Votes
FOR EACH ROW
BEGIN
    UPDATE Food_Items SET Vote_Count = GREATEST(Vote_Count - 1, 0)
    WHERE Item_ID = OLD.Food_ID;
END$$

CREATE TRIGGER trg_mess_off_check BEFORE INSERT ON Mess_Off
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    IF NEW.Status = 'Approved' THEN
        SELECT IFNULL(SUM(DATEDIFF(LEAST(End_Date, LAST_DAY(NEW.Start_Date)),
        GREATEST(Start_Date, DATE_FORMAT(NEW.Start_Date, '%Y-%m-01'))) + 1), 0)
        INTO v_count
        FROM Mess_Off
        WHERE User_ID = NEW.User_ID
        AND Status = 'Approved'
        AND Mess_Off_ID <> IFNULL(NEW.Mess_Off_ID, 0)
        AND Start_Date <= LAST_DAY(NEW.Start_Date)
        AND End_Date >= DATE_FORMAT(NEW.Start_Date, '%Y-%m-01');

        SET v_count = v_count + DATEDIFF(NEW.End_Date, NEW.Start_Date) + 1;
        IF v_count > 12 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Mess-off exceeds 12 days per month';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_mess_off_check_update BEFORE UPDATE ON Mess_Off
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    IF NEW.Status = 'Approved' AND (OLD.Status <> 'Approved' OR OLD.Start_Date <> NEW.Start_Date OR OLD.End_Date <> NEW.End_Date) THEN
        SELECT IFNULL(SUM(DATEDIFF(LEAST(End_Date, LAST_DAY(NEW.Start_Date)),
        GREATEST(Start_Date, DATE_FORMAT(NEW.Start_Date, '%Y-%m-01'))) + 1), 0)
        INTO v_count
        FROM Mess_Off
        WHERE User_ID = NEW.User_ID
        AND Status = 'Approved'
        AND Mess_Off_ID <> NEW.Mess_Off_ID
        AND Start_Date <= LAST_DAY(NEW.Start_Date)
        AND End_Date >= DATE_FORMAT(NEW.Start_Date, '%Y-%m-01');

        SET v_count = v_count + DATEDIFF(NEW.End_Date, NEW.Start_Date) + 1;
        IF v_count > 12 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Mess-off exceeds 12 days per month';
        END IF;
    END IF;
END$$

DELIMITER ;

# --- EVENTS ---

DROP EVENT IF EXISTS e_DailyOverdueCheck;
CREATE EVENT e_DailyOverdueCheck
ON SCHEDULE EVERY 1 DAY
STARTS (CURRENT_DATE + INTERVAL 1 DAY)
DO
  CALL sp_UpdateOverdueBills();

DROP EVENT IF EXISTS e_MonthlyBilling;
CREATE EVENT e_MonthlyBilling
ON SCHEDULE EVERY 1 MONTH
STARTS '2026-07-01 00:00:00'
DO
  CALL sp_GenerateMonthlyBills(DATE_SUB(CURDATE(), INTERVAL 1 MONTH));


# --- DUMMY DATA SEEDING ---

# 1. Users
INSERT INTO Users (UserID, First_Name, Last_Name, Email, Account_Type) VALUES
(1, 'Muhammad', 'Azaan', 'zainif63@gmail.com', 'Admin'),
(2, 'Muhammad', 'Azaan', 'mazaan.bscs25seecs@seecs.edu.pk', 'Student'),
(3, 'Jane', 'Smith', 'jane.student@seecs.edu.pk', 'Student'),
(4, 'Muhammad', 'Azaan', 'zainif630@gmail.com', 'Staff'),
(5, 'Bob', 'Jones', 'bob.student@seecs.edu.pk', 'Student'),
(6, 'Alice', 'Staff', 'alice.staff@seecs.edu.pk', 'Staff'),
(7, 'Charlie', 'Chef', 'charlie.chef@seecs.edu.pk', 'Staff');

# 2. Student Details
INSERT INTO Student (UserID, DoB, Department, Contact_Number, Address, Father_Name, Hostel_Name, Room_Number) VALUES
(2, '2004-05-15', 'CS', '0300-1234567', 'H-12 NUST', 'John Smith', 'Ghazali', '101'),
(3, '2003-11-20', 'SE', '0300-7654321', 'H-12 NUST', 'Mike Jones', 'Rumi', '202'),
(5, '2004-01-10', 'EE', '0321-9876543', 'H-12 NUST', 'David Jones', 'Attar', '303');

# 3. Staff Categories
INSERT INTO Staff_Category (Category, Working_hours, Salary) VALUES
('Chef', 8.0, 50000.00),
('Server', 6.0, 30000.00);

# 4. Staff Details
INSERT INTO Staff (UserID, Category) VALUES
(4, 'Server'),
(6, 'Chef');

# 5. Ingredients
INSERT INTO Ingredients (Name, Unit, Unit_cost, Total_Quantity) VALUES
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

# 6. Food Items
INSERT INTO Food_Items (Name, Quantity, Price) VALUES
('Chicken Biryani', 1.0, 250.00),
('Daal Mash', 1.0, 150.00),
('Special Tea', 1.0, 50.00),
('Aloo Paratha', 1.0, 80.00),
('Chicken Karahi', 1.0, 450.00),
('Mixed Vegetable', 1.0, 120.00),
('Roti', 1.0, 15.00);

# 7. Recipes
INSERT INTO Food_Item_Ingredients (Item_ID, Ingredient_ID, Ingredient_Quantity) VALUES
(1, 1, 0.5), (1, 2, 0.3), (1, 3, 0.1),
(2, 5, 0.4), (2, 3, 0.05),
(4, 10, 0.2), (4, 3, 0.01),
(5, 2, 0.5), (5, 3, 0.1), (5, 6, 0.1), (5, 7, 0.05),
(6, 6, 0.2), (6, 7, 0.1), (6, 3, 0.05),
(7, 10, 0.15);

# 8. Menu Schedule
INSERT INTO Menu_Schedule (Date, meal_type, status) VALUES
(CURDATE(), 'Breakfast', 'Active'),
(CURDATE(), 'Lunch', 'Active'),
(CURDATE(), 'Dinner', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Breakfast', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Lunch', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Dinner', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Breakfast', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Lunch', 'Active'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Dinner', 'Active');

# 9. Menu Mapping
INSERT INTO Menu_Food_Items (Schedule_ID, Item_ID) VALUES
(1, 3), (2, 1), (3, 2),
(4, 4), (4, 3),
(5, 5), (5, 7),
(6, 6), (6, 7),
(7, 4), (7, 3),
(8, 1), (8, 7),
(9, 2), (9, 7);

# 10. Mess Off Requests
INSERT INTO Mess_Off (User_ID, Start_Date, End_Date, Status) VALUES
(2, DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Pending'),
(3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Approved');

# 11. Bills
INSERT INTO Bills (User_ID, Amount, Due_Date, Month, Status) VALUES
(2, 4500.00, DATE_ADD(CURDATE(), INTERVAL 10 DAY), '2026-05-01', 'Unpaid'),
(3, 3800.00, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '2026-05-01', 'Overdue'),
(2, 4200.00, DATE_SUB(CURDATE(), INTERVAL 30 DAY), '2026-04-01', 'Paid');

# 12. Transactions
INSERT INTO Transactions (Billing_ID, Amount_Paid, Payment_Method, Transaction_Status) VALUES
(3, 4200.00, 'Online', 'Success');

# 13. Ratings
INSERT INTO Ratings (User_ID, Item_ID, Schedule_ID, Score) VALUES
(2, 1, 2, 5),
(3, 1, 2, 4),
(2, 3, 1, 3);

# 14. Votes
INSERT INTO Votes (User_ID, Food_ID) VALUES
(2, 1),
(3, 5),
(2, 5);