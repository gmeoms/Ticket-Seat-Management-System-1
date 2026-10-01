# DBMS Demo Guide

## Recommended 5-minute demonstration

1. Start MySQL Server.
2. Start the terminal application.
3. **View Customers** — demonstrates SELECT.
4. **View Events / Shows** — demonstrates joins.
5. **Check Seat Availability** — demonstrates joins and booking-state logic.
6. **Book Tickets** — demonstrates INSERT + transaction across:
   - bookings
   - booking_seats
   - payments
   - tickets
7. **View Booking** — demonstrates multi-table JOIN and GROUP_CONCAT.
8. **Cancel Booking** — demonstrates UPDATE.
9. **View Ticket** — demonstrates ticket retrieval.
10. Open MySQL Workbench and show the actual tables/records.

## DBMS concepts to mention

- Primary keys identify records.
- Foreign keys maintain relationships.
- UNIQUE constraints prevent duplicate email, phone and ticket codes.
- Normalized tables separate users, events, shows, seats, bookings and payments.
- Transactions keep booking-related inserts consistent.
- JOIN operations combine normalized data for reports.
- Indexes improve lookup by foreign keys and show dates.

## Suggested viva questions

### Why is booking_seats a separate table?
Because one booking can contain multiple seats and a seat can be booked for different shows. It represents the booking-to-seat relationship.

### Why is show different from event?
An event is the actual movie/concert/etc. A show is a scheduled occurrence of that event at a particular screen, date and time.

### Why are seats linked to screens?
Seat layouts belong to a physical screen. A show uses a screen, so the application can determine which seats are valid.

### Why use a transaction while booking?
Booking, seat allocation, payment and ticket creation should either all succeed or all fail.

### What happens when a booking is cancelled?
The booking status changes to `CANCELLED`. The terminal application's availability logic ignores cancelled bookings, so those seats become available again.

### What is the role of MySQL Workbench?
It is a GUI client used to inspect and manage the MySQL server. The application itself connects directly to MySQL.
