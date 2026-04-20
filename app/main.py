from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from app.db import get_conn, create_schema

app = FastAPI()

origins = ["*"] # Change to the real front end origin in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_schema()

# datamodell för bokning
class Booking(BaseModel):
    guest_id: int
    room_id: int
    datefrom: date 
    dateto: date

# Main route for this API
@app.get("/")
def read_root(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version() ")
        result = cur.fetchone()

    return { "msg": f"Hotel API!", "db_status": result }

# List all guests 
@app.get("/guests")
def get_rooms(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT g.*,
                (SELECT count(*) 
                    FROM bookings
                    WHERE guest_id = g.id
                        AND dateto < now()) AS prev_visits
            FROM guests g
            ORDER BY g.lastname
        """)
        guests = cur.fetchall()
    return guests
        
    
# List all rooms 
@app.get("/rooms")
def get_rooms(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM rooms
            ORDER BY room_number
        """)
        rooms = cur.fetchall()
    return rooms

# Get one room
@app.get("/rooms/{id}")
def get_room(id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM rooms 
            WHERE id = %s
        """, [id]) # list här, tuple används också
        room = cur.fetchone()
    return room      


# List all bookings 
@app.get("/bookings")
def get_bookings(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT 
                r.room_number,
                g.firstname || ' ' || g.lastname AS guest_name,
                (b.dateto - b.datefrom) AS nights,
                r.price as price_per_night,
                CASE 
                    WHEN (b.dateto - b.datefrom) >= 7 THEN 
                        -- 20 percent discount
                        (b.dateto - b.datefrom) * r.price * 0.8
                    ELSE (b.dateto - b.datefrom) * r.price
                END as total_price,
                b.*
            FROM bookings b
            INNER JOIN rooms r
                ON r.id = b.room_id
            INNER JOIN guests g
                ON g.id = b.guest_id
            ORDER BY id
        """)
        bookings = cur.fetchall()
    return bookings

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO bookings (
                guest_id,
                room_id,
                datefrom,
                dateto
            ) VALUES (
                %s, %s, %s, %s
            ) RETURNING id
        """, (
            booking.guest_id, 
            booking.room_id,
            booking.datefrom,
            booking.dateto
        ))
        new_booking = cur.fetchone()
    return { "msg": "Booking created!", "id": new_booking['id']}



