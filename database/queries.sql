USE ticket_seat_management;

-- 1. View all customers
SELECT * FROM users ORDER BY user_id;

-- 2. View events
SELECT event_id, event_name, event_type, duration_minutes
FROM events
ORDER BY event_id;

-- 3. View shows with venue and screen
SELECT
    s.show_id,
    e.event_name,
    v.venue_name,
    sc.screen_name,
    s.show_date,
    s.start_time,
    s.base_price,
    s.status
FROM shows s
JOIN events e ON e.event_id = s.event_id
JOIN screens sc ON sc.screen_id = s.screen_id
JOIN venues v ON v.venue_id = sc.venue_id
ORDER BY s.show_date, s.start_time;

-- 4. View all seats for a screen
SELECT *
FROM seats
WHERE screen_id = 1
ORDER BY seat_row, seat_number;

-- 5. Find booked seats for a show
SELECT
    b.show_id,
    CONCAT(se.seat_row, se.seat_number) AS seat,
    b.booking_id,
    b.booking_status
FROM booking_seats bs
JOIN bookings b ON b.booking_id = bs.booking_id
JOIN seats se ON se.seat_id = bs.seat_id
WHERE b.show_id = 1
  AND b.booking_status <> 'CANCELLED'
ORDER BY se.seat_row, se.seat_number;

-- 6. Booking details
SELECT
    b.booking_id,
    u.full_name,
    e.event_name,
    s.show_date,
    s.start_time,
    b.booking_status,
    b.total_amount
FROM bookings b
JOIN users u ON u.user_id = b.user_id
JOIN shows s ON s.show_id = b.show_id
JOIN events e ON e.event_id = s.event_id
ORDER BY b.booking_id;

-- 7. Payment details
SELECT *
FROM payments
ORDER BY payment_id;

-- 8. Ticket details
SELECT *
FROM tickets
ORDER BY ticket_id;

-- 9. Database statistics
SELECT 'users' AS table_name, COUNT(*) AS total FROM users
UNION ALL SELECT 'venues', COUNT(*) FROM venues
UNION ALL SELECT 'screens', COUNT(*) FROM screens
UNION ALL SELECT 'seats', COUNT(*) FROM seats
UNION ALL SELECT 'events', COUNT(*) FROM events
UNION ALL SELECT 'shows', COUNT(*) FROM shows
UNION ALL SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL SELECT 'booking_seats', COUNT(*) FROM booking_seats
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'tickets', COUNT(*) FROM tickets;
