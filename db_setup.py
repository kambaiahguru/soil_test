import sqlite3

def setup_db():
    # Connect to SQLite database
    conn = sqlite3.connect('soil_recommendation.db')
    cursor = conn.cursor()

    # Create tables (converted from MySQL to SQLite)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soiltypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        soil_name TEXT UNIQUE NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        soil_id INTEGER,
        FOREIGN KEY (soil_id) REFERENCES soiltypes(id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crop_nutrients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER,
        nutrient TEXT NOT NULL,
        ideal_value REAL NOT NULL,
        FOREIGN KEY (crop_id) REFERENCES crops(id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fertilizers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nutrient TEXT NOT NULL,
        fertilizer_name TEXT NOT NULL,
        quantity_per_deficiency REAL NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    ''')

    # Insert initial data into tables (same as before)
    # Insert data for soiltypes, crops, crop_nutrients, fertilizers, and users...

    # Commit and close the connection
    conn.commit()
    conn.close()

# Call the setup function
setup_db()
