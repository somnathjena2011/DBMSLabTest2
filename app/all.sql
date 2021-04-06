CREATE DATABASE labtest;

USE labtest;

CREATE TABLE user(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password VARCHAR(500) NOT NULL
);

CREATE TABLE room(
    room_id INT AUTO_INCREMENT,
    room_type VARCHAR(20),
    charge DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(room_id,room_type)
);

CREATE TABLE booking(
    booking_id INT AUTO_INCREMENT,
    user_id INT,
    room_id INT,
    room_type VARCHAR(20),
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    booked BOOLEAN DEFAULT FALSE,
    pending BOOLEAN DEFAULT FALSE,
    people INT,
    description VARCHAR(200),
    PRIMARY KEY(booking_id, user_id, room_id, room_type),
    FOREIGN KEY(user_id) REFERENCES user(user_id),
    FOREIGN KEY(room_id, room_type) REFERENCES room(room_id,room_type)
);

INSERT INTO room(room_type,charge) VALUES('A',50000.00);
INSERT INTO room(room_type,charge) VALUES('A',40000.00);
INSERT INTO room(room_type,charge) VALUES('A',5000.00);
INSERT INTO room(room_type,charge) VALUES('A',60000.00);
INSERT INTO room(room_type,charge) VALUES('B',50000.00);
INSERT INTO room(room_type,charge) VALUES('B',40000.00);
INSERT INTO room(room_type,charge) VALUES('B',5000.00);
INSERT INTO room(room_type,charge) VALUES('B',60000.00);

DROP TABLE user;
DROP TABLE room;
DROP TABLE booking;