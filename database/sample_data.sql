USE ticket_seat_management;

INSERT INTO users (full_name, email, phone) VALUES
('Aarav Sharma', 'aarav@example.com', '9876500001'),
('Priya Verma', 'priya@example.com', '9876500002'),
('Rahul Mehta', 'rahul@example.com', '9876500003');

INSERT INTO venues (venue_name, city, address) VALUES
('City Centre Multiplex', 'Bhopal', 'MP Nagar, Bhopal'),
('Grand Arena', 'Indore', 'Vijay Nagar, Indore');

INSERT INTO screens (venue_id, screen_name, total_seats) VALUES
(1, 'Screen 1', 16),
(1, 'Screen 2', 16),
(2, 'Main Arena', 16);

-- 16 seats per screen = 48 seats total.
-- Rows A-D, seats 1-4.
INSERT INTO seats (screen_id, seat_row, seat_number, seat_type)
SELECT 1, r.seat_row, n.seat_number,
       CASE
           WHEN r.seat_row = 'A' THEN 'PREMIUM'
           ELSE 'REGULAR'
       END
FROM
    (SELECT 'A' AS seat_row UNION ALL SELECT 'B' UNION ALL SELECT 'C' UNION ALL SELECT 'D') r
CROSS JOIN
    (SELECT 1 AS seat_number UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) n;

INSERT INTO seats (screen_id, seat_row, seat_number, seat_type)
SELECT 2, r.seat_row, n.seat_number,
       CASE
           WHEN r.seat_row = 'A' THEN 'PREMIUM'
           ELSE 'REGULAR'
       END
FROM
    (SELECT 'A' AS seat_row UNION ALL SELECT 'B' UNION ALL SELECT 'C' UNION ALL SELECT 'D') r
CROSS JOIN
    (SELECT 1 AS seat_number UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) n;

INSERT INTO seats (screen_id, seat_row, seat_number, seat_type)
SELECT 3, r.seat_row, n.seat_number,
       CASE
           WHEN r.seat_row = 'A' THEN 'PREMIUM'
           ELSE 'REGULAR'
       END
FROM
    (SELECT 'A' AS seat_row UNION ALL SELECT 'B' UNION ALL SELECT 'C' UNION ALL SELECT 'D') r
CROSS JOIN
    (SELECT 1 AS seat_number UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) n;

INSERT INTO events (event_name, event_type, duration_minutes, description) VALUES
('The Last Journey', 'MOVIE', 140, 'A fictional feature film for demonstration.'),
('Live Beats 2026', 'CONCERT', 120, 'A live music event for demonstration.');

INSERT INTO shows (event_id, screen_id, show_date, start_time, base_price, status) VALUES
(1, 1, '2026-10-10', '18:30:00', 250.00, 'SCHEDULED'),
(1, 1, '2026-10-11', '21:00:00', 300.00, 'SCHEDULED'),
(2, 3, '2026-10-12', '19:00:00', 800.00, 'SCHEDULED');
