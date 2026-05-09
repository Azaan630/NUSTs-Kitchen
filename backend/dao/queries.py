from main import request_mess_off

findUserByEmail = ("""SELECT *
                      FROM Users
                      WHERE Email = %s""")

getMenuByDate = ("""SELECT fi.Item_ID, fi.Name, fi.Ratings_Average, ms.Date
                    FROM Food_Items fi
                            JOIN Menu_Food_Items mfi ON fi.Item_ID = mfi.Item_ID
                            JOIN Menu_Schedule ms ON mfi.Schedule_ID = ms.Schedule_ID
                    WHERE ms.Date = %s""")

getWeeklyMenu = ("""SELECT fi.Item_ID, fi.Name, fi.Ratings_Average, ms.Date
                    FROM Food_Items fi
                             JOIN Menu_Food_Items mfi ON fi.Item_ID = mfi.Item_ID
                             JOIN Menu_Schedule ms ON mfi.Schedule_ID = ms.Schedule_ID
                    WHERE ms.Date BETWEEN %s AND DATE_ADD(%s, INTERVAL 7 DAY)
                    ORDER BY ms.DATE """)

getAllUsers = ("""SELECT * 
                  FROM Users""")

getMyBills = ("""SELECT *
                 FROM Bills
                    JOIN Users ON Users.UserID = Bills.User_ID
                 WHERE Email = %s
                 ORDER BY Issue_Date""")

getStudentBillDetails = ("""SELECT Users.First_Name, Users.First_Name, Bills.User_ID, Bills.Billing_ID, Bills.Month, Bills.Amount, Bills.Due_Date, Bills.Status
                            FROM Bills JOIN Users ON Users.UserID = Bills.User_ID
                            WHERE Bills.User_ID = %s""")

getIngredients = ("""SELECT *
                     FROM Ingredients""")

registerUser = ("""INSERT INTO Users
                      (First_Name, Last_Name, Email, Account_Type)
                      VALUES (%s, %s, %s, %s)""")

registerStudent = ("""INSERT INTO Student
                      (UserID, DoB, Department, Contact_Number, Address, Father_Name, Hostel_Name, Room_Number)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")

createBill = ("""INSERT INTO Bills
                 (User_ID, Issue_Date, Amount, Due_Date, Month, Status)
                 VALUES (%s, %s, %s, %s, %s, %s)""")

createFood = ("""INSERT INTO Food_Items
                 (Name, Quantity, Item_Expenditure)
                 VALUES (%s, %s, %s)""")

createIngredient = ("""INSERT INTO Ingredients
                       (Name, Total_Quantity, Pricing)
                       VALUES (%s, %s, %s)""")

registerStaff = ("""INSERT INTO Staff
                      (UserID, Category)
                      VALUES (%s, %s)""")

getStaffDetails = ("""SELECT *
                      FROM vw_StaffDetails WHERE UserID = %s""")

AddStaffContactNumber = ("""INSERT INTO Staff_Contact_Numbers
                            (UserID, Contact_Number)
                            VALUES (%s, %s)""")

addRecipe = ("""INSERT INTO Food_Item_Ingredients
                (Ingredient_ID, Ingredient_Quantity)
                VALUES (%s, %s)""")


getFoodByID = ("""SELECT 1
                  FROM Food_Items
                  WHERE ItemID = %s""")


addStaffCategory = """INSERT INTO StaffCategories
                      (Category, Working_hours, Salary)
                      VALUES (%s, %s, %s)"""


addMenuItem = """INSERT INTO Menu_Food_Items
                 (Schedule_ID, Item_ID)
                 VALUES (%s, %s)"""

getAllFoodCosts = ("""SELECT *
                      FROM vw_FoodItemCost""")

getWeeklyMenu = ("""SELECT * 
                    FROM vw_MenuSchedule
                    WHERE Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                    ORDER BY Date ASC, meal_type;""")

getMonthBills = ("""SELECT *
                    FROM vw_MonthlyBillingSummary""")

getCurrentScheduleID = ("""SELECT Schedule_ID
                           FROM Menu_Schedule
                           WHERE Date = %s AND meal_type = %s""")

giveFoodRating = ("""INSERT INTO Ratings
                     (User_ID, Item_ID, ScheduleID, Score)
                     VALUES (%s, %s, %s, %s)""")

getFoodRating = ("""SELECT
                    fi.Item_ID,
                    fi.Name,
                    fi.Ratings_Average AS Avg_Rating,
                    (SELECT COUNT(*) FROM Ratings r WHERE r.Item_ID = fi.Item_ID) AS Rating_Count,
                    fi.Vote_Count
                    FROM Food_Items fi
                    JOIN Menu_Food_Items mfi
                    WHERE mfi.Schedule_ID = %s AND mfi.Item_ID = %s;""")

requestMessOff = """INSERT INTO MessOff
                    (User_ID, Start_Date, End_Date)
                    VALUES (%s, %s, %s)"""

cancelMessOff = ("""DELETE FROM MessOff WHERE Mess_Off_ID = %s AND Status = 'Pending'""")

getMessOffStatus = ("""SELECT *
                       FROM MessOff WHERE Mess_Off_ID = %s""")

getBillPDF = ("""SELECT b.Billing_ID, b.Amount, b.Due_Date, b.Month, u.First_Name, u.Last_Name
                 FROM Bills b
                 JOIN Users u ON b.User_ID = u.UserID
                 WHERE b.Billing_ID = %s AND u.Email = %s""")