DROP DATABASE IF EXISTS `Imagestorage`;
create database Imagestorage;

--CREATE USER 'imgstore_user'@'%' IDENTIFIED BY 'password';
--GRANT ALL PRIVILEGES ON * . * TO 'imgstore_user'@'%';

use Imagestorage;

--CREATE USER 'imagestorage_user'@'%' IDENTIFIED BY 'password';
--GRANT ALL PRIVILEGES ON * . * TO 'imagestorage_user'@'%';

CREATE TABLE ImageOwners (
    OID int NOT NULL,
    FacebookID int,
    PRIMARY KEY (OID)
);

CREATE TABLE ImageData (
    ImageID int NOT NULL,
    Image varchar(255),
    TimeStamp TIMESTAMP DEFAULT (STRFTIME('%Y-%m-%d %H:%m:%S', 'NOW')),
    OwnerID int,
    PRIMARY KEY (ImageID),
    FOREIGN KEY (OwnerID) REFERENCES ImageOwners(OID)
);

INSERT INTO ImageOwners
    (OID,FacebookID)
VALUES
    (1, 34983984),
    (2, 37438784),
    (3, 93849344);
  
INSERT INTO ImageData
    (ImageID,Image,OwnerID)
VALUES
    (1, '/data/imageblobs/img1.jpg', 1),
    (2, '/data/imageblobs/img2.jpg', 1),
    (3, '/data/imageblobs/img3.jpg', 1),
    (4, '/data/imageblobs/img4.jpg', 1),
    (5, '/data/imageblobs/img5.jpg', 1),
    (6, '/data/imageblobs/img6.jpg', 1),
    (7, '/data/imageblobs/img7.jpg', 1),
    (8, '/data/imageblobs/img8.jpg', 1),
    (9, '/data/imageblobs/img9.jpg', 1),
    (10, '/data/imageblobs/img10.jpg', 1),
    (11, '/data/imageblobs/img11.jpg', 2),
    (12, '/data/imageblobs/img12.jpg', 2),
    (13, '/data/imageblobs/img13.jpg', 2),
    (14, '/data/imageblobs/img14.jpg', 2),
    (15, '/data/imageblobs/img15.jpg', 2),
    (16, '/data/imageblobs/img16.jpg', 2),
    (17, '/data/imageblobs/img17.jpg', 2),
    (18, '/data/imageblobs/img18.jpg', 2),
    (19, '/data/imageblobs/img19.jpg', 2),
    (20, '/data/imageblobs/img20.jpg', 2),
    (21, '/data/imageblobs/img21.jpg', 2),
    (22, '/data/imageblobs/img22.jpg', 3),
    (23, '/data/imageblobs/img23.jpg', 3),
    (24, '/data/imageblobs/img24.jpg', 3),
    (25, '/data/imageblobs/img25.jpg', 3),
    (26, '/data/imageblobs/img26.jpg', 3),
    (27, '/data/imageblobs/img27.jpg', 3),
    (28, '/data/imageblobs/img28.jpg', 3),
    (29, '/data/imageblobs/img29.jpg', 3),
    (30, '/data/imageblobs/img30.jpg', 3),
    (31, '/data/imageblobs/img31.jpg', 3),
    (32, '/data/imageblobs/img32.jpg', 3),
    (33, '/data/imageblobs/img33.jpg', 3);