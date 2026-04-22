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
            ALTER TABLE guests 
                ADD COLUMN IF NOT EXISTS api_key VARCHAR 
                DEFAULT encode(gen_random_bytes(32), 'hex');
                    
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
            ALTER TABLE bookings ADD COLUMN IF NOT EXISTS stars INT;
                    
            -- man kan sätta default också senare:
            -- ALTER TABLE bookings ALTER COLUMN datefrom SET DEFAULT now();
            -- lägg till främmande nyckel senare:
            -- ALTER TABLE bookings ADD CONSTRAINT guest_id_key FOREIGN KEY (guest_id) REFERENCES guests(id);

        """)
        print("DB schema created")

        cur.execute("""
            DROP VIEW bookings_view; 
            CREATE VIEW bookings_view AS
                SELECT 
                    r.room_number,
                    r.room_type,
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
                    ON g.id = b.guest_id;

            CREATE OR REPLACE VIEW guests_view AS
                SELECT g.id, 
                    g.firstname, 
                    g.lastname, 
                    g.address,
                    (SELECT count(*) 
                        FROM bookings
                        WHERE guest_id = g.id
                            AND dateto < now()) AS prev_visits
                FROM guests g
        """)
        print("DB views created")