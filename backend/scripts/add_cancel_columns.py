import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.sql import text
from app.database import DATABASE_URL

def add_cancel_columns():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Checking for new columns in 'sales' table...")
        
        # Check if columns exist
        try:
            connection.execute(text("SELECT status FROM sales LIMIT 1"))
            print("Column 'status' already exists.")
        except Exception as e:
            print(f"Adding column 'status'... ({e})")
            try:
                connection.execute(text("ALTER TABLE sales ADD COLUMN status VARCHAR(20) DEFAULT 'completed' NOT NULL"))
                print("Added 'status'")
            except Exception as e2:
                print(f"Failed to add status: {e2}")
            
        try:
            connection.execute(text("SELECT cancelled_at FROM sales LIMIT 1"))
            print("Column 'cancelled_at' already exists.")
        except Exception as e:
            print(f"Adding column 'cancelled_at'... ({e})")
            try:
                connection.execute(text("ALTER TABLE sales ADD COLUMN cancelled_at DATETIME"))
                print("Added 'cancelled_at'")
            except Exception as e2:
                print(f"Failed to add cancelled_at: {e2}")
            
        connection.commit()
        print("Migration complete.")

if __name__ == "__main__":
    add_cancel_columns()
