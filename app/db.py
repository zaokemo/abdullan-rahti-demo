import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        # Create the schema
        cur.execute("""
                    
            -- Lägg till pgcrypto 
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
                    
            -----------
            -- rooms
            -----------
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                room_number INT NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );       
            -- add columns
            ALTER TABLE rooms ADD COLUMN IF NOT EXISTS room_type VARCHAR;
            ALTER TABLE rooms ADD COLUMN IF NOT EXISTS price NUMERIC;

            -----------
            -- guests
            -----------
            CREATE TABLE IF NOT EXISTS guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR NOT NULL,
                lastname VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT now(),
                address VARCHAR
            );
            ALTER TABLE guests ADD COLUMN api_key VARCHAR DEFAULT encode(gen_random_bytes(32), 'hex');
                    
            -----------
            -- bookings
            -----------    
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT REFERENCES guests(id), -- foreign key (främmande nyckel)
                room_id INT REFERENCES rooms(id),
                datefrom DATE DEFAULT now(),
                dateto DATE,
                info VARCHAR
            );
            -- man kan sätta default också senare:
            -- ALTER TABLE bookings ALTER COLUMN datefrom SET DEFAULT now();
            -- lägg till främmande nyckel senare:
            -- ALTER TABLE bookings ADD CONSTRAINT guest_id_key FOREIGN KEY (guest_id) REFERENCES guests(id);



        """)
