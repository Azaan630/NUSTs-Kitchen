-- 1. Create and Use the Database
CREATE DATABASE IF NOT EXISTS mess_db;
USE mess_db;

-- 2. Create the Uses Table
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
('Azaan', 'Muhammad', 'azaan@nust.edu.pk', 'admin123', 'Admin'),
('Bob', 'Khan', 'farhad@nust.edu.pk', 'student123', 'Student');

INSERT INTO Food_Items (Name, Description, Price)
VALUES
('Chicken Biryani', 'Spicy Sindhi style biryani with raita', 250.00),
('Daal Mash', 'Traditional butter-tempered lentils', 120.00),
('Aloo Palak', 'Fresh spinach with sautéed potatoes', 150.00);

CREATE TABLE IF NOT EXISTS Users (
    UserID      INT PRIMARY KEY AUTO_INCREMENT,
    First_Name  VARCHAR(50) NOT NULL,
    Last_Name   VARCHAR(50) NOT NULL,
    Email       VARCHAR(100) UNIQUE NOT NULL,
    Password    VARCHAR(255) NOT NULL,
    Account_Type ENUM('Student', 'Staff') NOT NULL
);

CREATE TABLE IF NOT EXISTS Student (
    UserID          INT PRIMARY KEY,
    DoB             DATE,
    Department      VARCHAR(100),
    Contact_Number  VARCHAR(20),
    Address         TEXT,
    Father_Name     VARCHAR(100),
    Hostel_Name     VARCHAR(100),
    Room_Number     VARCHAR(20),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Staff (
    UserID          INT PRIMARY KEY,
    Category        VARCHAR(50),
    Working_Hours   DECIMAL(5,2),
    Salary          DECIMAL(10,2),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

-- Multivalued attribute — separate table
CREATE TABLE IF NOT EXISTS Staff_Contact_Numbers (
    Contact_ID      INT PRIMARY KEY AUTO_INCREMENT,
    UserID          INT NOT NULL,
    Contact_Number  VARCHAR(20) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Staff(UserID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Ingredients (
    Ingredient_ID   INT PRIMARY KEY AUTO_INCREMENT,
    Name            VARCHAR(100) NOT NULL,
    Total_Quantity  DECIMAL(10,2),
    Pricing         DECIMAL(10,2)
);


CREATE TABLE IF NOT EXISTS Food_Items (
    Item_ID             INT PRIMARY KEY AUTO_INCREMENT,
    Name                VARCHAR(100) NOT NULL,
    Quantity            DECIMAL(10,2),
    Day_Cooked_On       DATE,
    Ratings_Average     DECIMAL(3,2) DEFAULT 0.00,
    Vote_Count          INT DEFAULT 0,
    Item_Expenditure    DECIMAL(10,2),
    day varchar(30)
);


CREATE TABLE IF NOT EXISTS Food_Item_Ingredients (
    Item_ID         INT NOT NULL,
    Ingredient_ID   INT NOT NULL,
    PRIMARY KEY (Item_ID, Ingredient_ID),
    FOREIGN KEY (Item_ID)       REFERENCES Food_Items(Item_ID)      ON DELETE CASCADE,
    FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Menu_Schedule (
    Schedule_ID INT PRIMARY KEY AUTO_INCREMENT,
    Day         VARCHAR(20) NOT NULL,
    Date        DATE NOT NULL
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
    Request_Date    DATE NOT NULL,
    Status          ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Ratings (
    Rating_ID   INT PRIMARY KEY AUTO_INCREMENT,
    User_ID     INT NOT NULL,
    Item_ID     INT NOT NULL,
    Score       DECIMAL(3,2) NOT NULL CHECK (Score BETWEEN 1 AND 5),
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE,
    FOREIGN KEY (Item_ID) REFERENCES Food_Items(Item_ID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Votes (
    Vote_ID     INT PRIMARY KEY AUTO_INCREMENT,
    User_ID     INT NOT NULL,
    Food_ID     INT NOT NULL,
    Date_Time   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Student(UserID)    ON DELETE CASCADE,
    FOREIGN KEY (Food_ID) REFERENCES Food_Items(Item_ID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Bills (
    Billing_ID      INT PRIMARY KEY AUTO_INCREMENT,
    User_ID         INT NOT NULL,
    Issue_Date      DATE NOT NULL,
    Amount          DECIMAL(10,2) NOT NULL,
    Extra_Fee       DECIMAL(10,2) DEFAULT 0.00,
    Due_Date        DATE NOT NULL,
    Month           VARCHAR(20) NOT NULL,
    Status          ENUM('Paid', 'Unpaid', 'Overdue') DEFAULT 'Unpaid',
    FOREIGN KEY (User_ID) REFERENCES Student(UserID) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Transactions (
    Transaction_ID      INT NOT NULL,           -- Partial key (not unique alone)
    Billing_ID          INT NOT NULL,           -- FK from owner entity Bills
    Amount_Paid         DECIMAL(10,2) NOT NULL,
    Payment_Date        DATE NOT NULL,
    Payment_Method      VARCHAR(50),
    Transaction_Status  ENUM('Success', 'Failed', 'Pending') DEFAULT 'Pending',

    PRIMARY KEY (Billing_ID, Transaction_ID),   -- Composite PK (weak entity)
    FOREIGN KEY (Billing_ID) REFERENCES Bills(Billing_ID) ON DELETE CASCADE
);