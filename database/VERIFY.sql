USE ticket_seat_management;

SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'venues', COUNT(*) FROM venues
UNION ALL SELECT 'screens', COUNT(*) FROM screens
UNION ALL SELECT 'seats', COUNT(*) FROM seats
UNION ALL SELECT 'events', COUNT(*) FROM events
UNION ALL SELECT 'shows', COUNT(*) FROM shows
UNION ALL SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL SELECT 'booking_seats', COUNT(*) FROM booking_seats
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'tickets', COUNT(*) FROM tickets;

-- Check that every screen's declared capacity matches its seat count.
SELECT
    sc.screen_id,
    sc.screen_name,
    sc.total_seats,
    COUNT(se.seat_id) AS actual_seats,
    CASE WHEN sc.total_seats = COUNT(se.seat_id) THEN 'OK' ELSE 'CHECK' END AS result
FROM screens sc
LEFT JOIN seats se ON se.screen_id = sc.screen_id
GROUP BY sc.screen_id, sc.screen_name, sc.total_seats;
