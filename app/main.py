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

@app.get("/if/{term}")
def if_test(term: str):
    ret_str = "Default message..."
    if (term == "hello" 
        or term == "hi" 
        or term == "greetings"):
        
        ret_str = "Hello yourself!"
    elif (term == "morjens" or term == "hej") and 1 == 0:
        ret_str = "Hej på dig"
    else:
        ret_str = f"vad betyder {term}?"

    return { "msg": ret_str }
        
    
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
            SELECT * 
            FROM bookings
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