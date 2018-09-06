import os
from pathlib import Path

import sqlite3

from datetime import datetime


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory.parent / 'test/data/sqlite'
    return p / db_name


heartbit = target_file('heartbit.db')
if not heartbit.parent.exists():
    heartbit.parent.mkdir(parents=True)
if heartbit.exists():
    heartbit.unlink()

conn = sqlite3.connect(str(heartbit))
curr = conn.cursor()
current_date1 = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def create_table_heartbit():
    curr.execute('CREATE TABLE IF NOT EXISTS Users('
                 'ID int NOT NULL,'
                 'LastName varchar(255) NOT NULL,'
                 'FirstName varchar(255),'
                 'Email varchar(255),'
                 'GenderCode int,'
                 'PRIMARY KEY (ID))')

    curr.execute('CREATE TABLE IF NOT EXISTS UserData('
                 'DataID int NOT NULL,'
                 'Heartrate int,'
                 'GeoLocation int,'
                 'TimeStamp TIMESTAMP DEFAULT "{}",'
                 'Pulse int,'
                 'UserID int NOT NULL,'
                 'PRIMARY KEY (DataID),'
                 'FOREIGN KEY (UserID) REFERENCES Users(ID))'.format(current_date1))

def insert_value_heartbit():
    curr.execute("INSERT INTO Users(ID,LastName,FirstName,Email) VALUES (1,'McLean','Shawn','syonara@hotmail.com'),(2,'Hodge','Paul','paul@hotmail.com'),(3,'Ney','Ma','neyma@hotmail.com')")
    curr.execute("INSERT INTO UserData (DataID,Heartrate,GeoLocation,Pulse,UserID)"
                 "VALUES"
                 "(1,223,224344,12,1),"
                 "(2,228,22432,1,1),"
                 "(3,229,231387,11,1),"
                 "(4,243,232113,17,1),"
                 "(5,223,23213,19,1),"
                 "(6,223,25421,14,1),"
                 "(7,111,224321,9,1),"
                 "(8,118,224321,2,1),"
                 "(9,998,224321,187,1),"
                 "(10,776,224311,32,1),"
                 "(11,121,876522,99,1),"
                 "(12,228,224321,108,2),"
                 "(13,213,2871321,44,2),"
                 "(14,334,281398,65,2),"
                 "(15,875,224354,98,2),"
                 "(16,983,224331,22,2),"
                 "(17,111,22431,33,2),"
                 "(18,191,224385,18,2),"
                 "(19,181,224321,21,2),"
                 "(20,171,28721,97,3),"
                 "(21,223,224383,101,2),"
                 "(22,228,224311,87,2),"
                 "(23,333,224344,86,2),"
                 "(25,213,223417,38,3),"
                 "(26,999,224362,17,3),"
                 "(27,991,224352,14,3),"
                 "(28,872,222153,121,3),"
                 "(29,346,224342,141,3),"
                 "(30,298,224352,191,3),"
                 "(31,219,229852,107,3),"
                 "(32,217,224353,191,3)")
    conn.commit()
    curr.close()
    conn.close()

create_table_heartbit()
insert_value_heartbit()

datablob = target_file('datablob.db')
if not datablob.parent.exists():
    datablob.parent.mkdir(parents=True)
if datablob.exists():
    datablob.unlink()

conn = sqlite3.connect(str(datablob))
curr = conn.cursor()
current_date2 = datetime.now().strftime('%m/%d/%Y')


def create_table_Blob():
    curr.execute('CREATE TABLE IF NOT EXISTS BlobCreator ('
                 'CID int NOT NULL,'
                 'Name varchar(255),'
                 'PRIMARY KEY (CID))')
    curr.execute('CREATE TABLE IF NOT EXISTS BlobData ('
                 'BlobID int NOT NULL,'
                 'DataBlob BLOB,'
                 'BlobSize int,'
                 'TimeStamp TIMESTAMP DEFAULT "{}",'
                 'CreatorID int,'
                 'PRIMARY KEY (BlobID),'
                 'FOREIGN KEY (CreatorID) REFERENCES BlobCreator(CID))'.format(current_date2))


def insert_value_blob():
    curr.execute('INSERT INTO BlobCreator'
                 '(CID,Name)'
                 'VALUES'
                 '(1, "Shawn"),' 
                 '(2, "Nwahs"),'
                 '(3, "Pickleman")')
    curr.execute('INSERT INTO BlobData'
                 '(BlobID, BlobSize, DataBlob, CreatorID)'
                 'VALUES'
                 '(1, 40, "4D2AFF4D2AFF4D2AFF4D2AFF", 1),'
                 '(2, 50, "4D2AFF4DFF4D2AFF", 1),'
                 '(3, 89, "4D2AFF4D2AFF4D2AFF4D2AFFBDC2F21", 1),'
                 '(4, 101, "2AFF2AFF2AFF4D2AFF4D2AFF4D2AFF4D2AFF", 1),'
                 '(5, 12, "2AFF2AFF2AFF2AFF2AFF4D2AFF4D2AFF4D2AFF4D2AFF", 2),'
                 '(6, 45, "4D2AFF4D2AFF4BCCAAAD2AFF4D2AFF", 2),'
                 '(7, 98, "CCAAAD2ACCAAAD2ACCAAAD2A4D2AFF4D2AFF4D2AFF4D2AFF", 2),'
                 '(8, 93, "CCAAAD2ACCAAAD2A4D2AFF4D2AFF4D2AFF4D2AFFCCAAAD2ACCAAAD2A", 2),'
                 '(9, 111, "4D2AFF4D2AFF4D2AFF4D2AFF", 2),'
                 '(10, 12, "2ACCAAAD2AACCAAAD2A4D2AFF4D2AFF4D2AFF4D2AFF", 3),'
                 '(11, 65, "4D2AFF4D2AFF4D2AFF4D2AFF", 3),'
                 '(12, 87, "CCAAAD2A2ACCAAAD2A2ACCAAAD2A4D2AFF4D2AFF4D2AFF4D2AFF", 3),'
                 '(13, 91, "4D2AFF4D2AFF4D2AFF4D2AFF", 3),'
                 '(14, 103, "4ACCAAAD2A4D2A2AFF4D2ACCAAAD2A4D2AACCAAAD2A4D2AACCAAAD2A4D2A2AFF", 3),'
                 '(15, 143, "4D2AFACCAAAD2A4D2AACCAAAD2A4D2AF4D2AFF4D2AFF", 3),'
                 '(16, 985, "42ACCAAAD2A2ACCAAAD2A2ACCAAAD2AF4D2AFF4D2AFF4D2AFF", 3);')

    conn.commit()
    curr.close()
    conn.close()


create_table_Blob()
insert_value_blob()

imagestorage = target_file('imagestorage.db')
if not imagestorage.parent.exists():
    imagestorage.parent.mkdir(parents=True)
if imagestorage.exists():
    imagestorage.unlink()

conn = sqlite3.connect(str(imagestorage))
curr = conn.cursor()

current_date3 = datetime.now().strftime('%Y-%m-%d')


def create_table_imagestorage():
    curr.execute('CREATE TABLE IF NOT EXISTS ImageOwners ('
                 'OID int NOT NULL,'
                 'FacebookID int,'
                 'PRIMARY KEY (OID))')
    curr.execute('CREATE TABLE IF NOT EXISTS ImageData ('
                 'ImageID int NOT NULL,'
                 'Image varchar(255),'
                 'TimeStamp TEXT DEFAULT "{}",'
                 'OwnerID int,'
                 'PRIMARY KEY (ImageID),'
                 'FOREIGN KEY (OwnerID) REFERENCES ImageOwners(OID))'.format(current_date3))


def insert_value_imagestorage():
    curr.execute('INSERT INTO ImageOwners'
                 '(OID,FacebookID)'
                 'VALUES'
                 '(1, 34983984),'
                 '(2, 37438784),'
                 '(3, 93849344)')
    curr.execute('INSERT INTO ImageData'
                 '(ImageID,Image,OwnerID)'
                 'VALUES'
                 '(1, "/data_sources/imageblobs/img1.jpg", 1),'
                 '(2, "/data_sources/imageblobs/img2.jpg", 1),'
                 '(3, "/data_sources/imageblobs/img3.jpg", 1),'
                 '(4, "/data_sources/imageblobs/img4.jpg", 1),'
                 '(5, "/data_sources/imageblobs/img5.jpg", 1),'
                 '(6, "/data_sources/imageblobs/img6.jpg", 1),'
                 '(7, "/data_sources/imageblobs/img7.jpg", 1),'
                 '(8, "/data_sources/imageblobs/img8.jpg", 1),'
                 '(9, "/data_sources/imageblobs/img9.jpg", 1),'
                 '(10, "/data_sources/imageblobs/img10.jpg", 1),'
                 '(11, "/data_sources/imageblobs/img11.jpg", 2),'
                 '(12, "/data_sources/imageblobs/img12.jpg", 2),'
                 '(13, "/data_sources/imageblobs/img13.jpg", 2),'
                 '(14, "/data_sources/imageblobs/img14.jpg", 2),'
                 '(15, "/data_sources/imageblobs/img15.jpg", 2),'
                 '(16, "/data_sources/imageblobs/img16.jpg", 2),'
                 '(17, "/data_sources/imageblobs/img17.jpg", 2),'
                 '(18, "/data_sources/imageblobs/img18.jpg", 2),'
                 '(19, "/data_sources/imageblobs/img19.jpg", 2),'
                 '(20, "/data_sources/imageblobs/img20.jpg", 2),'
                 '(21, "/data_sources/imageblobs/img21.jpg", 2),'
                 '(22, "/data_sources/imageblobs/img22.jpg", 3),'
                 '(23, "/data_sources/imageblobs/img23.jpg", 3),'
                 '(24, "/data_sources/imageblobs/img24.jpg", 3),'
                 '(25, "/data_sources/imageblobs/img25.jpg", 3),'
                 '(26, "/data_sources/imageblobs/img26.jpg", 3),'
                 '(27, "/data_sources/imageblobs/img27.jpg", 3),'
                 '(28, "/data_sources/imageblobs/img28.jpg", 3),'
                 '(29, "/data_sources/imageblobs/img29.jpg", 3),'
                 '(30, "/data_sources/imageblobs/img30.jpg", 3),'
                 '(31, "/data_sources/imageblobs/img31.jpg", 3),'
                 '(32, "/data_sources/imageblobs/img32.jpg", 3),'
                 '(33, "/data_sources/imageblobs/img33.jpg", 3)')
    conn.commit()
    curr.close()
    conn.close()


create_table_imagestorage()
insert_value_imagestorage()




