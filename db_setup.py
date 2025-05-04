import sqlite3

def setup_db():
    """Sets up the SQLite database with all required tables and initial data."""
    conn = sqlite3.connect('soil_recommendation.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soiltypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        soil_name TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        soil_id INTEGER,
        FOREIGN KEY (soil_id) REFERENCES soiltypes(id)
    )
    ''')

    # Insert initial data
    cursor.execute("SELECT COUNT(*) FROM soiltypes")
    if cursor.fetchone()[0] == 0:
        soils = [
            ("Black Soil",), ("Laterite Soil",), ("Red Soil",),
            ("Alluvial Soil",), ("Clay Soil",), ("Sandy Soil",), ("Loamy Soil",)
        ]
        cursor.executemany("INSERT INTO soiltypes (soil_name) VALUES (?)", soils)

    cursor.execute("SELECT COUNT(*) FROM crops")
    if cursor.fetchone()[0] == 0:
        crops = [
            ("Rice", 1), ("Cotton", 1), ("Sugarcane", 1),  # Black Soil
            ("Tea", 2), ("Coffee", 2), ("Rubber", 2),      # Laterite Soil
            ("Groundnut", 3), ("Millets", 3), ("Tobacco", 3),  # Red Soil
            ("Wheat", 4), ("Rice", 4), ("Sugarcane", 4),    # Alluvial Soil
            ("Paddy", 5), ("Jute", 5), ("Wheat", 5),        # Clay Soil
            ("Coconut", 6), ("Groundnut", 6), ("Maize", 6),  # Sandy Soil
            ("Wheat", 7), ("Cotton", 7), ("Vegetables", 7)   # Loamy Soil
        ]
        cursor.executemany("INSERT INTO crops (crop_name, soil_id) VALUES (?, ?)", crops)

    conn.commit()
    conn.close()
