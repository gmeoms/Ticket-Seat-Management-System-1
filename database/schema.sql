-- Ticket & Seat Management System
-- Database schema for MySQL 8.x
-- Safe for a fresh installation. The terminal application expects this schema.

CREATE DATABASE IF NOT EXISTS ticket_seat_management;
USE ticket_seat_management;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS booking_seats;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS shows;
DROP TABLE IF EXISTS seats;
DROP TABLE IF EXISTS screens;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(15) UNIQUE,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
) ENGINE=InnoDB;

CREATE TABLE venues (
    venue_id INT NOT NULL AUTO_INCREMENT,
    venue_name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    address VARCHAR(255) NOT NULL,
    PRIMARY KEY (venue_id)
) ENGINE=InnoDB;

CREATE TABLE screens (
    screen_id INT NOT NULL AUTO_INCREMENT,
    venue_id INT NOT NULL,
    screen_name VARCHAR(80) NOT NULL,
    total_seats INT NOT NULL,
    PRIMARY KEY (screen_id),
    INDEX idx_screens_venue (venue_id),
    CONSTRAINT fk_screens_venue
        FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE seats (
    seat_id INT NOT NULL AUTO_INCREMENT,
    screen_id INT NOT NULL,
    seat_row CHAR(2) NOT NULL,
    seat_number INT NOT NULL,
    seat_type ENUM('REGULAR','PREMIUM','RECLINER') DEFAULT 'REGULAR',
    PRIMARY KEY (seat_id),
    INDEX idx_seats_screen (screen_id),
    CONSTRAINT fk_seats_screen
        FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_screen_seat UNIQUE (screen_id, seat_row, seat_number)
) ENGINE=InnoDB;

CREATE TABLE events (
    event_id INT NOT NULL AUTO_INCREMENT,
    event_name VARCHAR(150) NOT NULL,
    event_type ENUM('MOVIE','CONCERT','SPORT','THEATRE','OTHER') NOT NULL,
    duration_minutes INT,
    description TEXT,
    PRIMARY KEY (event_id)
) ENGINE=InnoDB;

CREATE TABLE shows (
    show_id INT NOT NULL AUTO_INCREMENT,
    event_id INT NOT NULL,
    screen_id INT NOT NULL,
    show_date DATE NOT NULL,
    start_time TIME NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    status ENUM('SCHEDULED','CANCELLED','COMPLETED') DEFAULT 'SCHEDULED',
    PRIMARY KEY (show_id),
    INDEX idx_shows_event (event_id),
    INDEX idx_shows_screen_date (screen_id, show_date),
    CONSTRAINT fk_shows_event
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_shows_screen
        FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE bookings (
    booking_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    show_id INT NOT NULL,
    booking_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    booking_status ENUM('PENDING','CONFIRMED','CANCELLED') DEFAULT 'PENDING',
    total_amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (booking_id),
    INDEX idx_bookings_user (user_id),
    INDEX idx_bookings_show (show_id),
    CONSTRAINT fk_bookings_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_show
        FOREIGN KEY (show_id) REFERENCES shows(show_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE booking_seats (
    booking_seat_id INT NOT NULL AUTO_INCREMENT,
    booking_id INT NOT NULL,
    seat_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (booking_seat_id),
    INDEX idx_booking_seats_booking (booking_id),
    INDEX idx_booking_seats_seat (seat_id),
    CONSTRAINT fk_booking_seats_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_booking_seats_seat
        FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE payments (
    payment_id INT NOT NULL AUTO_INCREMENT,
    booking_id INT NOT NULL UNIQUE,
    payment_method ENUM('CARD','UPI','NET_BANKING','CASH') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('PENDING','SUCCESS','FAILED','REFUNDED') DEFAULT 'PENDING',
    paid_at TIMESTAMP NULL,
    PRIMARY KEY (payment_id),
    CONSTRAINT fk_payments_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE tickets (
    ticket_id INT NOT NULL AUTO_INCREMENT,
    booking_id INT NOT NULL,
    ticket_code VARCHAR(30) NOT NULL UNIQUE,
    issued_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticket_id),
    INDEX idx_tickets_booking (booking_id),
    CONSTRAINT fk_tickets_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;
