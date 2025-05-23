# db_setup.py
import sqlite3

def setup_db():
    """Initialize database with all required tables and sample data"""
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect('soil_recommendation.db')
        cursor = conn.cursor()

        # Create tables with error handling
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )""",
            'soiltypes': """
                CREATE TABLE IF NOT EXISTS soiltypes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soil_name TEXT UNIQUE NOT NULL
                )""",
            'crops': """
                CREATE TABLE IF NOT EXISTS crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_name TEXT NOT NULL,
                    soil_id INTEGER NOT NULL,
                    FOREIGN KEY (soil_id) REFERENCES soiltypes(id)
                )"""
        }

        for table, schema in tables.items():
            cursor.execute(schema)

        # Insert soil types if empty
        cursor.execute("SELECT COUNT(*) FROM soiltypes")
        if cursor.fetchone()[0] == 0:
            soils = [
                ('Black Soil',), ('Laterite Soil',), ('Red Soil',),
                ('Alluvial Soil',), ('Clay Soil',), ('Sandy Soil',),
                ('Loamy Soil',)
            ]
            cursor.executemany("INSERT INTO soiltypes (soil_name) VALUES (?)", soils)

        # Insert crops if empty
        cursor.execute("SELECT COUNT(*) FROM crops")
        if cursor.fetchone()[0] == 0:
            crops = [
                ('Rice', 1), ('Cotton', 1), ('Sugarcane', 1),
                ('Tea', 2), ('Coffee', 2), ('Rubber', 2),
                ('Groundnut', 3), ('Millets', 3), ('Tobacco', 3),
                ('Wheat', 4), ('Rice', 4), ('Sugarcane', 4),
                ('Paddy', 5), ('Jute', 5), ('Wheat', 5),
                ('Coconut', 6), ('Groundnut', 6), ('Maize', 6),
                ('Wheat', 7), ('Cotton', 7), ('Vegetables', 7)
            ]
            cursor.executemany("INSERT INTO crops (crop_name, soil_id) VALUES (?, ?)", crops)

        conn.commit()
        print("Database setup completed successfully")
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()  # Rollback changes on error
        raise
    finally:
        pass # Connection is returned, closing is handled in app.py

if __name__ == "__main__":
    setup_db()
