from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, conint
from datetime import date
from app.db import get_conn, create_schema
from markupsafe import escape

# OBS: Lektion 8, API kräver nu API-nyckel
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

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail={"error": "API key missing"})
    
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM guests WHERE api_key = %s
        """, [api_key])
        guest = cur.fetchone()
        if not guest:
            raise HTTPException(status_code=401, detail={"error": "Bad API Key"})
        return guest
        

# datamodell för ny bokning
class Booking(BaseModel):
    #guest_id: int # kommer via api-ley i stället
    room_id: int
    datefrom: date 
    dateto: date
    info: str

# datamodell för uppdatera bokning
class BookingUpdate(BaseModel):
    stars: conint(ge=1, le=5) # tar emot int 1-5

# Main route for this API
@app.get("/")
def read_root(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version() ")
        result = cur.fetchone()

    return { "msg": f"Hotel API!", "db_status": result }


# List all guests 
@app.get("/guests")
def get_guests(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM guests_view
            ORDER BY lastname
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
def get_bookings(guest: dict = Depends(validate_api_key)): 
    print(guest)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM bookings_view
            WHERE guest_id = %s
            ORDER BY id DESC
        """, [guest['id']] )
        bookings = cur.fetchall()
        
    return bookings

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking, guest: dict = Depends(validate_api_key)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO bookings (
                guest_id,
                room_id,
                datefrom,
                dateto,
                info
            ) VALUES (
                %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            guest['id'], 
            booking.room_id,
            booking.datefrom,
            booking.dateto,
            escape(booking.info)
        ))
        new_booking = cur.fetchone()
    return { "msg": "Booking created!", "id": new_booking['id']}

# Update booking
@app.put("/bookings/{id}")
def update_booking(id: int, booking: BookingUpdate, 
    guest: dict = Depends(validate_api_key)):

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE bookings SET
                stars = %s
            WHERE id = %s
                AND guest_id = %s
            RETURNING *
        """, [booking.stars, id, guest['id']])
        updated_booking = cur.fetchone()
        if updated_booking:
            return { "msg": "booking updated!", "id": updated_booking['id']}
        else:
            raise HTTPException(status_code=404, detail={"error": "Booking not found"})