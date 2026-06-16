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

ALTER TABLE Registration_Requests
    ADD COLUMN Profile_Picture VARCHAR(500) DEFAULT NULL
    AFTER Category;

CREATE OR REPLACE VIEW vw_FoodItemCost AS
SELECT
    fi.Item_ID,
    fi.Name,
    fi.Image_Path,
    fi.Price,
    fi.Quantity,
    SUM(i.Unit_cost * fgi.Ingredient_Quantity) AS Total_Cost
FROM Food_Items fi
LEFT JOIN Food_Item_Ingredients fgi ON fi.Item_ID = fgi.Item_ID
LEFT JOIN Ingredients i ON fgi.Ingredient_ID = i.Ingredient_ID
GROUP BY fi.Item_ID, fi.Name, fi.Image_Path, fi.Price, fi.Quantity;

CREATE TABLE IF NOT EXISTS Feedback (
    Feedback_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name        VARCHAR(100),
    Email       VARCHAR(100),
    Subject     VARCHAR(200) NOT NULL,
    Message     TEXT NOT NULL,
    Created_At  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    Step_ID     INT PRIMARY KEY AUTO_INCREMENT,
    Item_ID     INT NOT NULL,
    Step_Number INT NOT NULL,
    Description TEXT NOT NULL,
    FOREIGN KEY (Item_ID) REFERENCES Food_Items(Item_ID) ON DELETE CASCADE
);
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
