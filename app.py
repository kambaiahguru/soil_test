import sqlite3
import os

def initialize_database():
    """Initialize or connect to the database with proper error handling"""
    db_path = 'soil_recommendation.db'
    is_new_db = not os.path.exists(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if is_new_db:
            # Create tables for new database
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE soiltypes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soil_name TEXT UNIQUE NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_name TEXT NOT NULL,
                    soil_id INTEGER NOT NULL,
                    FOREIGN KEY (soil_id) REFERENCES soiltypes(id)
                )
            ''')
            
            # Insert initial data
            soils = [
                ('Black Soil',), ('Laterite Soil',), ('Red Soil',),
                ('Alluvial Soil',), ('Clay Soil',), ('Sandy Soil',), 
                ('Loamy Soil',)
            ]
            cursor.executemany("INSERT INTO soiltypes (soil_name) VALUES (?)", soils)
            
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
            print("New database created and initialized successfully")
        else:
            print("Connected to existing database")
            
        return conn
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise

if __name__ == "__main__":
    initialize_database()
