import sqlite3

def migrate():
    conn = sqlite3.connect('instance/school.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE school_date (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                shift VARCHAR(50) NOT NULL,
                CONSTRAINT _date_shift_uc UNIQUE (date, shift)
            )
        """)
        print("Created school_date table")
    except sqlite3.OperationalError as e:
        print(f"Table might already exist: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
