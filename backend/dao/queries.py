findUserByEmail = ("""SELECT *
                      FROM Users
                      WHERE Email = %s""")

getMenuByDate = ("""SELECT fi.Item_ID, fi.Name, fi.Ratings_Average, ms.Date, ms.meal_type AS meal_type,
                           (SELECT Score FROM Ratings r WHERE r.User_ID = %s AND r.Item_ID = fi.Item_ID AND r.Schedule_ID = mfi.Schedule_ID LIMIT 1) AS user_rating
                    FROM Food_Items fi
                            JOIN Menu_Food_Items mfi ON fi.Item_ID = mfi.Item_ID
                            JOIN Menu_Schedule ms ON mfi.Schedule_ID = ms.Schedule_ID
                    WHERE ms.Date = %s""")

getWeeklyMenu = ("""SELECT fi.Item_ID, fi.Name, fi.Ratings_Average, ms.Date, ms.meal_type AS meal_type,
                           mfi.Schedule_ID,
                           (SELECT Score FROM Ratings r WHERE r.User_ID = %s AND r.Item_ID = fi.Item_ID AND r.Schedule_ID = mfi.Schedule_ID LIMIT 1) AS user_rating
                    FROM Food_Items fi
                             JOIN Menu_Food_Items mfi ON fi.Item_ID = mfi.Item_ID
                             JOIN Menu_Schedule ms ON mfi.Schedule_ID = ms.Schedule_ID
                    WHERE ms.Date >= %s AND ms.Date < DATE_ADD(%s, INTERVAL 7 DAY)
                    ORDER BY ms.Date""")

getAllUsers = ("""SELECT * 
                  FROM Users""")

getMyBills = ("""SELECT *
                 FROM Bills
                    JOIN Users ON Users.UserID = Bills.User_ID
                 WHERE Email = %s
                 ORDER BY Issue_Date""")

getStudentBillDetails = ("""SELECT Users.First_Name, Users.Last_Name, Bills.User_ID, Bills.Billing_ID, Bills.Month, Bills.Amount, Bills.Due_Date, Bills.Status,
                                   COALESCE(t.Total_Paid, 0) AS Total_Collected
                            FROM Bills
                            JOIN Users ON Users.UserID = Bills.User_ID
                            LEFT JOIN (
                                SELECT Billing_ID, SUM(Amount_Paid) AS Total_Paid
                                FROM Transactions
                                WHERE Transaction_Status = 'Success'
                                GROUP BY Billing_ID
                            ) t ON Bills.Billing_ID = t.Billing_ID
                            WHERE Bills.User_ID = %s""")

getIngredients = ("""SELECT *
                     FROM Ingredients""")

registerUser = ("""INSERT INTO Users
                      (First_Name, Last_Name, Email, Account_Type, Sex, Profile_Picture)
                      VALUES (%s, %s, %s, %s, %s, %s)""")

registerStudent = ("""INSERT INTO Student
                      (UserID, DoB, Department, Contact_Number, Address, Father_Name, Hostel_Name, Room_Number)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")

createBill = ("""INSERT INTO Bills
                 (User_ID, Issue_Date, Amount, Due_Date, Month, Status)
                 VALUES (%s, %s, %s, %s, %s, %s)""")

createFood = ("""INSERT INTO Food_Items
                 (Name, Quantity, Price)
                 VALUES (%s, %s, %s)""")

createIngredient = ("""INSERT INTO Ingredients
                       (Name, Unit, Unit_cost, Total_Quantity)
                       VALUES (%s, %s, %s, %s)""")

registerStaff = ("""INSERT INTO Staff
                      (UserID, Category)
                      VALUES (%s, %s)""")

getStaffDetails = ("""SELECT *
                      FROM vw_StaffDetails WHERE UserID = %s""")

getStudentDetails = ("""SELECT *
                        FROM vw_StudentDetails WHERE UserID = %s""")

AddStaffContactNumber = ("""INSERT INTO Staff_Contact_Numbers
                            (UserID, Contact_Number)
                            VALUES (%s, %s)""")

addRecipe = ("""INSERT INTO Food_Item_Ingredients
                (Item_ID, Ingredient_ID, Ingredient_Quantity)
                VALUES (%s, %s, %s)""")


getFoodByID = ("""SELECT *
                  FROM Food_Items
                  WHERE Item_ID = %s""")


addStaffCategory = """INSERT INTO Staff_Category
                      (Category, Working_hours, Salary)
                      VALUES (%s, %s, %s)"""

getAllStaffCategories = """SELECT * FROM Staff_Category"""

deleteStaffCategory = """DELETE FROM Staff_Category WHERE Category = %s"""


addMenuItem = """INSERT INTO Menu_Food_Items
                 (Schedule_ID, Item_ID)
                 VALUES (%s, %s)"""

getAllFoodCosts = ("""SELECT *
                      FROM vw_FoodItemCost""")

getAllFoodItems = ("""SELECT *
                      FROM Food_Items""")

getMonthBills = ("""SELECT *
                    FROM vw_MonthlyBillingSummary""")

getCurrentScheduleID = ("""SELECT Schedule_ID
                           FROM Menu_Schedule
                           WHERE Date = %s AND meal_type = %s""")

giveFoodRating = ("""REPLACE INTO Ratings
                     (User_ID, Item_ID, Schedule_ID, Score)
                     VALUES (%s, %s, %s, %s)""")

getFoodRating = ("""SELECT
                    fi.Item_ID,
                    fi.Name,
                    fi.Ratings_Average AS Avg_Rating,
                    (SELECT COUNT(*) FROM Ratings r WHERE r.Item_ID = fi.Item_ID) AS Rating_Count,
                    fi.Vote_Count
                    FROM Food_Items fi
                    JOIN Menu_Food_Items mfi ON fi.Item_ID = mfi.Item_ID
                    WHERE mfi.Schedule_ID = %s AND mfi.Item_ID = %s;""")

requestMessOff = """INSERT INTO Mess_Off
                    (User_ID, Start_Date, End_Date)
                    VALUES (%s, %s, %s)"""

cancelMessOff = ("""DELETE FROM Mess_Off WHERE Mess_Off_ID = %s AND Status = 'Pending'""")

getMessOffStatus = ("""SELECT *
                       FROM Mess_Off WHERE Mess_Off_ID = %s""")

getMessOffThisMonth = ("""SELECT *
                           FROM Mess_Off
                           WHERE (DATE(Start_Date) >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')
                               OR DATE(End_Date)   >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01'))
                           ORDER BY Start_Date DESC;""")

getMyMessOffThisMonth = ("""SELECT *
                            FROM Mess_Off
                            WHERE (DATE(Start_Date) >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')
                                OR DATE(End_Date)   >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01'))
                              AND User_ID = %s
                            ORDER BY Start_Date DESC;""")

getMessOffAdmin = ("""SELECT *
                          FROM Mess_Off 
                          JOIN Users ON Users.UserID = Mess_Off.User_ID
                          WHERE (
                          Start_Date >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') 
                          OR End_Date >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')
                          );""")

getBillPDF = ("""SELECT b.Billing_ID, b.Amount, b.Due_Date, b.Month, u.First_Name, u.Last_Name
                 FROM Bills b
                 JOIN Users u ON b.User_ID = u.UserID
                 WHERE b.Billing_ID = %s AND u.Email = %s""")

getRecipes = ("""SELECT Food_Item_Ingredients.Item_ID, Ingredients.Ingredient_ID, Ingredient_Quantity, Ingredients.Unit, Ingredients.Name
                 FROM Food_Item_Ingredients JOIN Ingredients ON Food_Item_Ingredients.Ingredient_ID = Ingredients.Ingredient_ID""")

getRecipesDetailed = ("""SELECT
    fi.Item_ID, fi.Name AS Item_Name, fi.Price,
    i.Ingredient_ID, i.Name AS Ingredient_Name,
    i.Unit, fii.Ingredient_Quantity, i.Total_Quantity AS Ingredient_Stock
FROM Food_Item_Ingredients fii
JOIN Food_Items fi ON fii.Item_ID = fi.Item_ID
JOIN Ingredients i ON fii.Ingredient_ID = i.Ingredient_ID
ORDER BY fi.Name, i.Name""")