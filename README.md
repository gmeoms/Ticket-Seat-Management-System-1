# Ticket & Seat Management System

A **MySQL + Python terminal-based DBMS project** for managing events, shows, screens, seats, customers, bookings, payments and tickets.

## Features

- View customers
- Add new customers
- View events
- View shows with venue, screen, date, time and price
- Check seat availability
- Interactive seat selection
- Book multiple seats
- Booking confirmation summary
- Transaction-safe booking
- Automatic payment record
- Automatic ticket generation
- View booking details
- Cancel booking
- View e-ticket
- Database statistics
- SQL schema, sample data and demonstration queries
- ER diagram and architecture diagram

## Technology Stack

- **Python 3**
- **MySQL 8.x**
- **mysql-connector-python**
- **SQL**
- **Git / GitHub**

## Database Design

The database contains these 10 tables:

| Table | Purpose |
|---|---|
| `users` | Customer information |
| `venues` | Physical venues |
| `screens` | Screens/arenas inside venues |
| `seats` | Seats belonging to screens |
| `events` | Movies, concerts, sports, theatre, etc. |
| `shows` | Scheduled occurrence of an event |
| `bookings` | Customer booking |
| `booking_seats` | Seats included in each booking |
| `payments` | Payment information |
| `tickets` | Generated ticket |

### ER Diagram

![ER Diagram](diagrams/ER_Diagram.png)

The same diagram is available as GitHub-rendered Mermaid in [`diagrams/ER_Diagram.md`](diagrams/ER_Diagram.md).

## Project Architecture

![Architecture](diagrams/Architecture.png)

## Database Relationships

- One **venue** has many **screens**.
- One **screen** has many **seats**.
- One **event** can have many **shows**.
- One **screen** can host many **shows**.
- One **user** can make many **bookings**.
- One **show** can have many **bookings**.
- One **booking** can contain many **booking_seats**.
- One **seat** can appear in many booking records across different shows.
- A booking can have one payment.
- A booking can generate one ticket.

## Setup

### 1. Start MySQL Server

Make sure your MySQL Server service is running.

### 2. Create the database

Open MySQL Workbench and run:

```sql
SOURCE path/to/database/schema.sql;
```

Or open `database/schema.sql` in Workbench and execute it.

### 3. Add sample data

Run:

```sql
SOURCE path/to/database/sample_data.sql;
```

### 4. Create the application user:

If you have not already created it:

```sql
CREATE USER 'ticket_app'@'localhost'
IDENTIFIED BY 'TicketApp@1234';

GRANT ALL PRIVILEGES
ON ticket_seat_management.*
TO 'ticket_app'@'localhost';

FLUSH PRIVILEGES;
```

### 5. Install Python dependency

From the project root:

```powershell
python -m pip install -r requirements.txt
```

### 6. Set database environment variables

PowerShell:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="ticket_app"
$env:MYSQL_PASSWORD="TicketApp@1234"
$env:MYSQL_DATABASE="ticket_seat_management"
```

### 7. Run

```powershell
python terminal_app\app.py
```

## Application Flow

### Book Tickets

The application guides the user through:

```text
Select Customer
       Γåô
Select Show
       Γåô
Display Seat Map
       Γåô
Select Available Seats
       Γåô
Show Booking Summary
       Γåô
Confirm
       Γåô
Create Booking
       Γåô
Create Booking Seats
       Γåô
Create Payment
       Γåô
Create Ticket
```

All booking-related inserts are performed in one database transaction.

## Example Menu

```text
========================================================================
                  TICKET & SEAT MANAGEMENT SYSTEM
========================================================================
1. View Customers
2. Add New Customer
3. View Events
4. View Shows
5. Check Seat Availability
6. Book Tickets
7. View Booking
8. Cancel Booking
9. View Ticket
10. Database Statistics
0. Exit
```

## Important DBMS Concepts Demonstrated

- Primary keys
- Foreign keys
- Candidate/unique keys
- Referential integrity
- Normalization
- SQL SELECT / INSERT / UPDATE
- Multi-table JOINs
- Aggregation
- Transactions
- Constraints
- Indexes
- One-to-many relationships
- Relationship/junction table design

## SQL Files

- [`database/schema.sql`](database/schema.sql) ΓÇö complete database structure
- [`database/sample_data.sql`](database/sample_data.sql) ΓÇö demo records
- [`database/queries.sql`](database/queries.sql) ΓÇö useful SQL queries
- [`database/VERIFY.sql`](database/VERIFY.sql) ΓÇö verification queries

## Documentation

- [`docs/DBMS_Demo_Guide.md`](docs/DBMS_Demo_Guide.md)
- [`docs/Project_Structure.md`](docs/Project_Structure.md)
- [`diagrams/ER_Diagram.md`](diagrams/ER_Diagram.md)
