create database Heartbit;

--CREATE USER 'heartbit_user'@'%' IDENTIFIED BY 'password';
--GRANT ALL PRIVILEGES ON * . * TO 'heartbit_user'@'%';

use Heartbit;

CREATE TABLE Users (
    ID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Email varchar(255),
    GenderCode int,
    PRIMARY KEY (ID)
);

CREATE TABLE UserData (
    DataID int NOT NULL,
    Heartrate int,
    GeoLocation int,
    TimeStamp TIMESTAMP DEFAULT (STRFTIME('%m-%d-%Y', 'NOW')),
    Pulse int,
    UserID int NOT NULL,
    PRIMARY KEY (DataID),
    FOREIGN KEY (UserID) REFERENCES Users(ID)
);

INSERT INTO Users
    (ID,LastName,FirstName,Email)
VALUES
    (1,'McLean','Shawn','syonara@hotmail.com'),
    (2,'Hodge','Paul','paul@hotmail.com'),
    (3,'Ney','Ma','neyma@hotmail.com');
  
INSERT INTO UserData
    (DataID,Heartrate,GeoLocation,Pulse,UserID)
VALUES
    (1,223,224344,12,1),
    (2,228,22432,1,1),
    (3,229,231387,11,1),
    (4,243,232113,17,1),
    (5,223,23213,19,1),
    (6,223,25421,14,1),
    (7,111,224321,9,1),
    (8,118,224321,2,1),
    (9,998,224321,187,1),
    (10,776,224311,32,1),
    (11,121,876522,99,1),
    (12,228,224321,108,2),
    (13,213,2871321,44,2),
    (14,334,281398,65,2),
    (15,875,224354,98,2),
    (16,983,224331,22,2),
    (17,111,22431,33,2),
    (18,191,224385,18,2),
    (19,181,224321,21,2),
    (20,171,28721,97,3),
    (21,223,224383,101,2),
    (22,228,224311,87,2),
    (23,333,224344,86,2),
    (24,896,224376,31,3),
    (25,213,223417,38,3),
    (26,999,224362,17,3),
    (27,991,224352,14,3),
    (28,872,222153,121,3),
    (29,346,224342,141,3),
    (30,298,224352,191,3),
    (31,219,229852,107,3),
    (32,217,224353,191,3);