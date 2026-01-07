import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        cursor.execute(schema_sql)
        conn.commit()
        print("Database schema initialized successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
