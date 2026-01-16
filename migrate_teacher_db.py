import sqlite3

def migrate():
    conn = sqlite3.connect('instance/school.db')
    cursor = conn.cursor()
    
    try:
        # Add phone column to teacher table
        cursor.execute("ALTER TABLE teacher ADD COLUMN phone VARCHAR(20)")
        print("Added phone column to teacher table")
    except sqlite3.OperationalError as e:
        print(f"Column might already exist: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
