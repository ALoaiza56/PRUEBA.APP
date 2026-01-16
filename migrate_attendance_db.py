import sqlite3

def migrate():
    conn = sqlite3.connect('instance/school.db')
    cursor = conn.cursor()
    
    try:
        # Create new table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                school_date_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                comment VARCHAR(200),
                FOREIGN KEY(student_id) REFERENCES student(id),
                FOREIGN KEY(school_date_id) REFERENCES school_date(id)
            )
        """)
        
        print("Created attendance table.")
        
    except Exception as e:
        print(f"Migration error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
