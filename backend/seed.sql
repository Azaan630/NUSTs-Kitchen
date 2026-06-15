CREATE TABLE IF NOT EXISTS Registration_Requests (
    RequestID      INT PRIMARY KEY AUTO_INCREMENT,
    First_Name     VARCHAR(50) NOT NULL,
    Last_Name      VARCHAR(50) NOT NULL,
    Email          VARCHAR(100) NOT NULL,
    Account_Type   ENUM('Student', 'Staff') NOT NULL,
    Sex            ENUM('Male', 'Female') DEFAULT NULL,
    DoB            DATE,
    Department     VARCHAR(100),
    Contact_Number VARCHAR(20),
    Address        TEXT,
    Father_Name    VARCHAR(100),
    Hostel_Name    VARCHAR(100),
    Room_Number    VARCHAR(20),
    Category       VARCHAR(30),
    Profile_Picture VARCHAR(500) DEFAULT NULL,
    Status         ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    Created_At     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO Users (UserID, First_Name, Last_Name, Email, Account_Type, Sex, Profile_Picture) VALUES
(1, 'Muhammad', 'Azaan', 'zainif63@gmail.com',              'Admin',   'Male', 'https://picsum.photos/seed/admin1/200/200'),
(2, 'Muhammad', 'Azaan', 'mazaan.bscs25seecs@seecs.edu.pk', 'Student', 'Male', 'https://picsum.photos/seed/student1/200/200'),
(3, 'Muhammad', 'Azaan', 'zainif630@gmail.com',             'Staff',   'Male', 'https://picsum.photos/seed/staff1/200/200');
