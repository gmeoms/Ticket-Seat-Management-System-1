
import os
from decimal import Decimal
import mysql.connector
from mysql.connector import Error


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "ticket_app"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "ticket_seat_management")
    )


def fetch_all(sql, params=()):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def header(title):
    print("\n" + "=" * 78)
    print(title.center(78))
    print("=" * 78)


def pause():
    input("\nPress Enter to return to the main menu...")


def ask_int(message):
    while True:
        value = input(message).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a number.")


# ============================================================
# DISPLAY / SELECTION HELPERS
# ============================================================

def choose_customer():
    customers = fetch_all("""
        SELECT user_id, full_name, email, phone
        FROM users
        ORDER BY user_id
    """)

    if not customers:
        print("No customers found.")
        return None

    print("\nCUSTOMERS")
    print("-" * 78)
    for c in customers:
        print(
            f"{c['user_id']:>2}. {c['full_name']:<22} "
            f"{c['email']:<28} {c['phone'] or '-'}"
        )

    while True:
        customer_id = ask_int("\nSelect Customer ID: ")
        selected = next((c for c in customers if c["user_id"] == customer_id), None)
        if selected:
            print(f"Selected: {selected['full_name']}")
            return selected
        print("Invalid Customer ID. Choose one from the list.")


def choose_show(include_price=True):
    shows = fetch_all("""
        SELECT
            s.show_id,
            e.event_name,
            v.venue_name,
            sc.screen_name,
            s.show_date,
            s.start_time,
            s.base_price
        FROM shows s
        JOIN events e ON e.event_id = s.event_id
        JOIN screens sc ON sc.screen_id = s.screen_id
        JOIN venues v ON v.venue_id = sc.venue_id
        ORDER BY s.show_date, s.start_time
    """)

    if not shows:
        print("No shows found.")
        return None

    print("\nAVAILABLE SHOWS")
    print("-" * 78)
    for s in shows:
        price = f"₹{s['base_price']}"
        print(
            f"{s['show_id']}. {s['event_name']} | "
            f"{s['show_date']} {str(s['start_time'])[:5]} | "
            f"{s['venue_name']} - {s['screen_name']} | {price}"
        )

    while True:
        show_id = ask_int("\nSelect Show ID: ")
        selected = next((s for s in shows if s["show_id"] == show_id), None)
        if selected:
            print(f"Selected: {selected['event_name']}")
            return selected
        print("Invalid Show ID. Choose one from the list.")


def get_show(show_id):
    result = fetch_all("""
        SELECT
            s.show_id,
            s.event_id,
            s.screen_id,
            s.show_date,
            s.start_time,
            s.base_price,
            e.event_name,
            e.event_type,
            sc.screen_name,
            v.venue_name
        FROM shows s
        JOIN events e ON e.event_id = s.event_id
        JOIN screens sc ON sc.screen_id = s.screen_id
        JOIN venues v ON v.venue_id = sc.venue_id
        WHERE s.show_id = %s
    """, (show_id,))
    return result[0] if result else None


def get_booked_seat_ids(show_id):
    rows = fetch_all("""
        SELECT bs.seat_id
        FROM booking_seats bs
        JOIN bookings b ON b.booking_id = bs.booking_id
        WHERE b.show_id = %s
          AND b.booking_status <> 'CANCELLED'
    """, (show_id,))
    return {row["seat_id"] for row in rows}


def get_available_seats(show_id):
    show = get_show(show_id)
    if not show:
        return None, []

    booked_ids = get_booked_seat_ids(show_id)

    seats = fetch_all("""
        SELECT seat_id, seat_row, seat_number, seat_type
        FROM seats
        WHERE screen_id = %s
        ORDER BY seat_row, seat_number
    """, (show["screen_id"],))

    available = [s for s in seats if s["seat_id"] not in booked_ids]
    return show, available


def display_seat_map(show_id, only_available=False):
    """Display a compact, readable 4-column seat map."""
    show, available = get_available_seats(show_id)

    if not show:
        print("Show not found.")
        return []

    all_seats = fetch_all("""
        SELECT seat_id, seat_row, seat_number, seat_type
        FROM seats
        WHERE screen_id = %s
        ORDER BY seat_row, seat_number
    """, (show["screen_id"],))

    booked_ids = get_booked_seat_ids(show_id)
    available_ids = {seat["seat_id"] for seat in available}

    print("\n" + "-" * 78)
    print(f"Event : {show['event_name']}")
    print(f"Date  : {show['show_date']}    Time: {str(show['start_time'])[:8]}")
    print(f"Venue : {show['venue_name']}    Screen: {show['screen_name']}")
    print(f"Price : ₹{show['base_price']}")
    print("-" * 78)

    print("\n" + "SCREEN".center(78))
    print("[ FRONT ]".center(78))
    print()

    # Group seats by row so every row is printed on its own line.
    rows = {}
    for seat in all_seats:
        rows.setdefault(seat["seat_row"], []).append(seat)

    print("       " + "    ".join(f"{('SEAT ' + str(i)):^10}" for i in range(1, 5)))
    print("       " + "    ".join("----------" for _ in range(4)))

    for row_name, row_seats in rows.items():
        cells = []
        for seat in row_seats:
            label = f"{seat['seat_row']}{seat['seat_number']}"
            status = "X" if seat["seat_id"] in booked_ids else "O"
            cells.append(f"[{label}:{status}]".center(10))
        while len(cells) < 4:
            cells.append("".center(10))
        print(f"Row {row_name}  " + "    ".join(cells))

    print("\n" + "-" * 78)
    print("O = AVAILABLE     X = BOOKED")
    print("Seat format: [A1:O]  = Row A, Seat 1, Available")

    total_count = len(all_seats)
    available_count = len(available)
    booked_count = len(booked_ids)
    print("-" * 78)
    print(
        f"SEAT SUMMARY   Total: {total_count}   "
        f"Available: {available_count}   Booked: {booked_count}"
    )

    if only_available:
        print("\nAVAILABLE SEATS")
        print("-" * 78)
        if not available:
            print("No seats are currently available for this show.")
        else:
            # Keep the list in compact columns to avoid ugly terminal wrapping.
            for i in range(0, len(available), 4):
                group = available[i:i + 4]
                parts = [
                    f"{seat['seat_row']}{seat['seat_number']} ({seat['seat_type']})"
                    for seat in group
                ]
                print("    ".join(f"{part:<20}" for part in parts))

    return available


def parse_seat_labels(text):
    labels = []
    for item in text.split(","):
        item = item.strip().upper().replace(" ", "")
        if item:
            labels.append(item)
    return labels


# ============================================================
# 1. CUSTOMERS
# ============================================================

def view_customers():
    header("CUSTOMERS")

    data = fetch_all("""
        SELECT user_id, full_name, email, phone
        FROM users
        ORDER BY user_id
    """)

    if not data:
        print("No customers found.")
        return

    print(f"{'ID':<5}{'NAME':<24}{'EMAIL':<30}{'PHONE'}")
    print("-" * 78)

    for r in data:
        print(
            f"{r['user_id']:<5}"
            f"{r['full_name']:<24}"
            f"{r['email']:<30}"
            f"{r['phone'] or '-'}"
        )


# ============================================================
# 2. ADD CUSTOMER
# ============================================================

def add_customer():
    header("ADD NEW CUSTOMER")

    name = input("Full name : ").strip()
    email = input("Email     : ").strip()
    phone = input("Phone     : ").strip()

    if not name or not email:
        print("Name and email are required.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (full_name, email, phone)
            VALUES (%s, %s, %s)
        """, (name, email, phone or None))

        connection.commit()
        print(f"\nCustomer added successfully!")
        print(f"Customer ID: {cursor.lastrowid}")

    except Error as e:
        connection.rollback()
        print(f"Could not add customer: {e}")

    finally:
        cursor.close()
        connection.close()


# ============================================================
# 3. EVENTS
# ============================================================

def view_events():
    header("EVENTS")

    data = fetch_all("""
        SELECT event_id, event_name, event_type, duration_minutes, description
        FROM events
        ORDER BY event_id
    """)

    for r in data:
        print(
            f"[{r['event_id']}] {r['event_name']} | "
            f"{r['event_type']} | {r['duration_minutes']} min"
        )
        if r["description"]:
            print(f"     {r['description']}")
        print()


# ============================================================
# 4. SHOWS
# ============================================================

def view_shows():
    header("SHOWS")
    choose_show()


# ============================================================
# 5. SEAT AVAILABILITY
# ============================================================

def view_seats():
    header("CHECK SEAT AVAILABILITY")

    show = choose_show()
    if not show:
        return

    display_seat_map(show["show_id"], only_available=True)


# ============================================================
# 6. BOOK SEATS - EASY FLOW
# ============================================================

def book_seats():
    header("BOOK TICKETS")

    print("STEP 1 OF 3: SELECT CUSTOMER")
    customer = choose_customer()
    if not customer:
        return

    print("\n" + "-" * 78)
    print("STEP 2 OF 3: SELECT SHOW")
    show = choose_show()
    if not show:
        return

    print("\n" + "-" * 78)
    print("STEP 3 OF 3: SELECT SEATS")
    available = display_seat_map(show["show_id"], only_available=True)

    if not available:
        print("\nNo seats are available for this show.")
        return

    valid_labels = {
        f"{s['seat_row']}{s['seat_number']}": s
        for s in available
    }

    print("\nExample: A3,A4,B1")
    while True:
        text = input("Enter seat(s): ")
        labels = parse_seat_labels(text)

        if not labels:
            print("Please enter at least one seat.")
            continue

        invalid = [x for x in labels if x not in valid_labels]
        duplicate = len(labels) != len(set(labels))

        if invalid:
            print("Invalid/unavailable seat(s):", ", ".join(invalid))
            print("Please choose from the AVAILABLE SEATS list.")
            continue

        if duplicate:
            print("You entered the same seat more than once.")
            continue

        break

    selected = [valid_labels[x] for x in labels]
    total = Decimal(str(show["base_price"])) * len(selected)

    print("\n" + "=" * 50)
    print("BOOKING SUMMARY".center(50))
    print("=" * 50)
    print(f"Customer : {customer['full_name']}")
    print(f"Event    : {show['event_name']}")
    print(f"Show     : {show['show_date']} {show['start_time']}")
    print(f"Venue    : {show['venue_name']}")
    print(f"Screen   : {show['screen_name']}")
    print(f"Seats    : {', '.join(labels)}")
    print(f"Total    : ₹{total}")
    print("=" * 50)

    confirm = input("Confirm booking? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Booking cancelled by user.")
        return

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        # Re-check seats inside the transaction.
        seat_ids = [s["seat_id"] for s in selected]
        placeholders = ",".join(["%s"] * len(seat_ids))

        cursor.execute(f"""
            SELECT bs.seat_id, se.seat_row, se.seat_number
            FROM booking_seats bs
            JOIN bookings b ON b.booking_id = bs.booking_id
            JOIN seats se ON se.seat_id = bs.seat_id
            WHERE b.show_id = %s
              AND b.booking_status <> 'CANCELLED'
              AND bs.seat_id IN ({placeholders})
            FOR UPDATE
        """, [show["show_id"], *seat_ids])

        busy = cursor.fetchall()

        if busy:
            names = ", ".join(
                f"{x['seat_row']}{x['seat_number']}" for x in busy
            )
            raise ValueError(f"These seats were just booked: {names}")

        cursor.execute("""
            INSERT INTO bookings
                (user_id, show_id, booking_status, total_amount)
            VALUES (%s, %s, 'CONFIRMED', %s)
        """, (customer["user_id"], show["show_id"], total))

        booking_id = cursor.lastrowid

        for seat in selected:
            cursor.execute("""
                INSERT INTO booking_seats
                    (booking_id, seat_id, price)
                VALUES (%s, %s, %s)
            """, (
                booking_id,
                seat["seat_id"],
                show["base_price"]
            ))

        cursor.execute("""
            INSERT INTO payments
                (booking_id, payment_method, amount, payment_status, paid_at)
            VALUES (%s, 'CASH', %s, 'SUCCESS', NOW())
        """, (booking_id, total))

        ticket_code = f"TKT-{booking_id:06d}"

        cursor.execute("""
            INSERT INTO tickets (booking_id, ticket_code)
            VALUES (%s, %s)
        """, (booking_id, ticket_code))

        connection.commit()

        print("\n" + "=" * 50)
        print("BOOKING SUCCESSFUL".center(50))
        print("=" * 50)
        print(f"Booking ID : {booking_id}")
        print(f"Ticket     : {ticket_code}")
        print(f"Seats      : {', '.join(labels)}")
        print(f"Total      : ₹{total}")
        print("=" * 50)

    except ValueError as e:
        connection.rollback()
        print(f"\nBooking failed: {e}")

    except Error as e:
        connection.rollback()
        print(f"\nDatabase error: {e}")

    finally:
        cursor.close()
        connection.close()


# ============================================================
# BOOKING LIST
# ============================================================

def list_bookings(include_cancelled=True):
    condition = "" if include_cancelled else "AND b.booking_status <> 'CANCELLED'"

    return fetch_all(f"""
        SELECT
            b.booking_id,
            u.full_name,
            e.event_name,
            s.show_date,
            s.start_time,
            b.booking_status,
            b.total_amount,
            t.ticket_code
        FROM bookings b
        JOIN users u ON u.user_id = b.user_id
        JOIN shows s ON s.show_id = b.show_id
        JOIN events e ON e.event_id = s.event_id
        LEFT JOIN tickets t ON t.booking_id = b.booking_id
        WHERE 1=1 {condition}
        ORDER BY b.booking_id DESC
    """)


def display_booking_list(bookings):
    if not bookings:
        print("No bookings found.")
        return

    print("\nBOOKINGS")
    print("-" * 78)

    for b in bookings:
        print(
            f"[{b['booking_id']}] "
            f"{b['full_name']} | "
            f"{b['event_name']} | "
            f"{b['show_date']} {str(b['start_time'])[:5]} | "
            f"₹{b['total_amount']} | "
            f"{b['booking_status']}"
        )


def choose_booking(include_cancelled=True):
    bookings = list_bookings(include_cancelled)

    if not bookings:
        return None

    display_booking_list(bookings)

    valid_ids = {b["booking_id"]: b for b in bookings}

    while True:
        booking_id = ask_int("\nSelect Booking ID: ")
        if booking_id in valid_ids:
            return valid_ids[booking_id]
        print("Invalid Booking ID. Choose one from the list.")


# ============================================================
# 7. VIEW BOOKING - EASY
# ============================================================

def view_booking():
    header("VIEW BOOKING")

    print("Select a booking from the list below.")
    booking = choose_booking()

    if not booking:
        return

    data = fetch_all("""
        SELECT
            b.booking_id,
            b.booking_time,
            b.booking_status,
            b.total_amount,
            u.full_name,
            u.email,
            e.event_name,
            s.show_date,
            s.start_time,
            v.venue_name,
            sc.screen_name,
            GROUP_CONCAT(
                CONCAT(se.seat_row, se.seat_number)
                ORDER BY se.seat_row, se.seat_number
                SEPARATOR ', '
            ) AS seats
        FROM bookings b
        JOIN users u ON u.user_id = b.user_id
        JOIN shows s ON s.show_id = b.show_id
        JOIN events e ON e.event_id = s.event_id
        JOIN screens sc ON sc.screen_id = s.screen_id
        JOIN venues v ON v.venue_id = sc.venue_id
        LEFT JOIN booking_seats bs ON bs.booking_id = b.booking_id
        LEFT JOIN seats se ON se.seat_id = bs.seat_id
        WHERE b.booking_id = %s
        GROUP BY
            b.booking_id, b.booking_time, b.booking_status,
            b.total_amount, u.full_name, u.email, e.event_name,
            s.show_date, s.start_time, v.venue_name, sc.screen_name
    """, (booking["booking_id"],))

    r = data[0]

    print("\n" + "=" * 55)
    print("BOOKING DETAILS".center(55))
    print("=" * 55)
    print(f"Booking ID : {r['booking_id']}")
    print(f"Customer   : {r['full_name']}")
    print(f"Email      : {r['email']}")
    print(f"Event      : {r['event_name']}")
    print(f"Venue      : {r['venue_name']}")
    print(f"Screen     : {r['screen_name']}")
    print(f"Show       : {r['show_date']} {r['start_time']}")
    print(f"Seats      : {r['seats'] or '-'}")
    print(f"Amount     : ₹{r['total_amount']}")
    print(f"Status     : {r['booking_status']}")
    print(f"Booked At  : {r['booking_time']}")
    print("=" * 55)


# ============================================================
# 8. CANCEL BOOKING - EASY
# ============================================================

def cancel_booking():
    header("CANCEL BOOKING")

    print("Only active bookings are shown.")
    booking = choose_booking(include_cancelled=False)

    if not booking:
        print("There are no active bookings.")
        return

    print("\nSelected booking:")
    print(f"Customer : {booking['full_name']}")
    print(f"Event    : {booking['event_name']}")
    print(f"Date     : {booking['show_date']} {booking['start_time']}")
    print(f"Amount   : ₹{booking['total_amount']}")

    confirm = input("\nCancel this booking? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Cancellation aborted.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'CANCELLED'
            WHERE booking_id = %s
              AND booking_status <> 'CANCELLED'
        """, (booking["booking_id"],))

        connection.commit()

        if cursor.rowcount:
            print("\nBooking cancelled successfully.")
            print("The seats are now available again.")

        else:
            print("Booking could not be cancelled.")

    except Error as e:
        connection.rollback()
        print(f"Could not cancel booking: {e}")

    finally:
        cursor.close()
        connection.close()


# ============================================================
# 9. VIEW TICKET - EASY
# ============================================================

def view_ticket():
    header("VIEW TICKET")

    print("Select a booking to view its ticket.")
    booking = choose_booking()

    if not booking:
        return

    data = fetch_all("""
        SELECT
            t.ticket_code,
            t.issued_at,
            b.booking_id,
            b.booking_status,
            b.total_amount,
            u.full_name,
            e.event_name,
            s.show_date,
            s.start_time,
            v.venue_name,
            sc.screen_name,
            GROUP_CONCAT(
                CONCAT(se.seat_row, se.seat_number)
                ORDER BY se.seat_row, se.seat_number
                SEPARATOR ', '
            ) AS seats
        FROM tickets t
        JOIN bookings b ON b.booking_id = t.booking_id
        JOIN users u ON u.user_id = b.user_id
        JOIN shows s ON s.show_id = b.show_id
        JOIN events e ON e.event_id = s.event_id
        JOIN screens sc ON sc.screen_id = s.screen_id
        JOIN venues v ON v.venue_id = sc.venue_id
        LEFT JOIN booking_seats bs ON bs.booking_id = b.booking_id
        LEFT JOIN seats se ON se.seat_id = bs.seat_id
        WHERE b.booking_id = %s
        GROUP BY
            t.ticket_code, t.issued_at, b.booking_id,
            b.booking_status, b.total_amount, u.full_name,
            e.event_name, s.show_date, s.start_time,
            v.venue_name, sc.screen_name
    """, (booking["booking_id"],))

    if not data:
        print("\nNo ticket exists for this booking.")
        return

    r = data[0]

    print("\n" + "=" * 58)
    print("E - TICKET".center(58))
    print("=" * 58)
    print(f"Ticket Code : {r['ticket_code']}")
    print(f"Customer    : {r['full_name']}")
    print(f"Event       : {r['event_name']}")
    print(f"Venue       : {r['venue_name']}")
    print(f"Screen      : {r['screen_name']}")
    print(f"Show        : {r['show_date']} {r['start_time']}")
    print(f"Seats       : {r['seats'] or '-'}")
    print(f"Amount      : ₹{r['total_amount']}")
    print(f"Status      : {r['booking_status']}")
    print(f"Issued      : {r['issued_at']}")
    print("=" * 58)


# ============================================================
# 10. DATABASE STATISTICS
# ============================================================

def statistics():
    header("DATABASE STATISTICS")

    tables = [
        ("Users", "users"),
        ("Venues", "venues"),
        ("Screens", "screens"),
        ("Seats", "seats"),
        ("Events", "events"),
        ("Shows", "shows"),
        ("Bookings", "bookings"),
        ("Booking Seats", "booking_seats"),
        ("Payments", "payments"),
        ("Tickets", "tickets"),
    ]

    connection = get_connection()
    cursor = connection.cursor()

    try:
        for label, table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"{label:<20}: {count}")
    finally:
        cursor.close()
        connection.close()


# ============================================================
# MAIN MENU
# ============================================================

def main():
    try:
        connection = get_connection()
        connection.close()
    except Error as e:
        print("Database connection failed:")
        print(e)
        return

    actions = {
        "1": view_customers,
        "2": add_customer,
        "3": view_events,
        "4": view_shows,
        "5": view_seats,
        "6": book_seats,
        "7": view_booking,
        "8": cancel_booking,
        "9": view_ticket,
        "10": statistics,
    }

    while True:
        header("TICKET & SEAT MANAGEMENT SYSTEM")

        print("1. View Customers")
        print("2. Add New Customer")
        print("3. View Events")
        print("4. View Shows")
        print("5. Check Seat Availability")
        print("6. Book Tickets")
        print("7. View Booking")
        print("8. Cancel Booking")
        print("9. View Ticket")
        print("10. Database Statistics")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            print("\nThank you for using Ticket & Seat Management System.")
            break

        action = actions.get(choice)

        if action:
            try:
                action()
            except Error as e:
                print(f"\nDatabase error: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")
            pause()
        else:
            print("Invalid choice.")
            pause()


if __name__ == "__main__":
    main()
