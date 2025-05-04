import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime

# Import the setup_db function from db_setup.py
try:
    from db_setup import setup_db
except ModuleNotFoundError:
    def setup_db():
        """Sets up the SQLite database with tables and initial data."""
        conn = connect_db()
        if conn is None:
            st.stop()
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Create soiltypes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soiltypes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soil_name TEXT UNIQUE NOT NULL
            )
        """)

        # Create crops table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL,
                soil_id INTEGER,
                FOREIGN KEY (soil_id) REFERENCES soiltypes (id)
            )
        """)

        # Insert initial data into soiltypes
        cursor.execute("SELECT COUNT(*) FROM soiltypes")
        if cursor.fetchone()[0] == 0:
            soils = [("Black Soil",), ("Laterite Soil",), ("Red Soil",), ("Alluvial Soil",),
                     ("Clay Soil",), ("Sandy Soil",), ("Loamy Soil",)]
            cursor.executemany("INSERT INTO soiltypes (soil_name) VALUES (?)", soils)

        # Insert initial data into crops
        cursor.execute("SELECT COUNT(*) FROM crops")
        if cursor.fetchone()[0] == 0:
            crops = [
                ("Rice", 1), ("Cotton", 1), ("Sugarcane", 1),
                ("Tea", 2), ("Coffee", 2), ("Rubber", 2),
                ("Groundnut", 3), ("Millets", 3), ("Tobacco", 3),
                ("Wheat", 4), ("Rice", 4), ("Sugarcane", 4),
                ("Paddy", 5), ("Jute", 5), ("Wheat", 5),
                ("Coconut", 6), ("Groundnut", 6), ("Maize", 6),
                ("Wheat", 7), ("Cotton", 7), ("Vegetables", 7)
            ]
            cursor.executemany("INSERT INTO crops (crop_name, soil_id) VALUES (?, ?)", crops)

        conn.commit()
        conn.close()
        print("Created database and populated with initial data")


# 🔗 Connect to SQLite
def connect_db():
    try:
        conn = sqlite3.connect('soil_recommendation.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None


# ✅ Run setup if database doesn't exist
if not os.path.exists('soil_recommendation.db'):
    setup_db()
    st.info("Database created and initial data loaded.")
else:
    st.info("Database file already exists.")


# 🔐 Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 🔍 Verify login
def verify_user(username, password):
    db = connect_db()
    if db is None:
        return False
    cursor = db.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    db.close()
    if user and user[2] == hash_password(password):
        st.session_state.user_id = user[0]
        return True
    return False


# 📝 Register user
def register_user(username, password):
    db = connect_db()
    if db is None:
        return False
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        st.error("Username already exists.")
        return False
    finally:
        db.close()


# 📥 Soil & Crop info
def get_soil_types():
    db = connect_db()
    if db is None:
        return []
    cursor = db.cursor()
    cursor.execute("SELECT id, soil_name FROM soiltypes")
    result = [{"id": row[0], "soil_name": row[1]} for row in cursor.fetchall()]
    db.close()
    return result


def get_crops_by_soil(soil_id):
    db = connect_db()
    if db is None:
        return []
    cursor = db.cursor()
    cursor.execute("SELECT id, crop_name FROM crops WHERE soil_id = ?", (soil_id,))
    result = [{"id": row[0], "crop_name": row[1]} for row in cursor.fetchall()]
    db.close()
    return result


# 🎯 Standard nutrients
standard_nutrients = {
    1: {"nitrogen": 50, "phosphorus": 30, "potassium": 40},
    2: {"nitrogen": 45, "phosphorus": 25, "potassium": 35},
    3: {"nitrogen": 60, "phosphorus": 40, "potassium": 50},
    4: {"nitrogen": 80, "phosphorus": 60, "potassium": 70},
    5: {"nitrogen": 70, "phosphorus": 55, "potassium": 65},
    6: {"nitrogen": 90, "phosphorus": 75, "potassium": 85},
    7: {"nitrogen": 85, "phosphorus": 70, "potassium": 80},
}


# ⚙️ Analyze soil
def analyze_soil(crop_id, n, p, k, T):
    std = standard_nutrients.get(crop_id)
    if not std:
        return None
    return {
        T["nitrogen"].split()[0].capitalize(): f"{T['excess_by']} {n - std['nitrogen']:.2f}" if n > std["nitrogen"]
        else f"{T['deficient_by']} {std['nitrogen'] - n:.2f}" if n < std["nitrogen"] else T["balanced"],
        T["phosphorus"].split()[0].capitalize(): f"{T['excess_by']} {p - std['phosphorus']:.2f}" if p > std["phosphorus"]
        else f"{T['deficient_by']} {std['phosphorus'] - p:.2f}" if p < std["phosphorus"] else T["balanced"],
        T["potassium"].split()[0].capitalize(): f"{T['excess_by']} {k - std['potassium']:.2f}" if k > std["potassium"]
        else f"{T['deficient_by']} {std['potassium'] - k:.2f}" if k < std["potassium"] else T["balanced"]
    }


# 💊 Recommend fertilizers
def recommend_fertilizer(crop_id, n, p, k, T):
    std = standard_nutrients.get(crop_id)
    if not std:
        return [], []

    deficiency = {
        "nitrogen": max(0, std["nitrogen"] - n),
        "phosphorus": max(0, std["phosphorus"] - p),
        "potassium": max(0, std["potassium"] - k),
    }

    fertilizers_data = [
        {"name": "Urea", "nitrogen": 46, "phosphorus": 0, "potassium": 0},
        {"name": "DAP", "nitrogen": 18, "phosphorus": 46, "potassium": 0},
        {"name": "MOP", "nitrogen": 0, "phosphorus": 0, "potassium": 60},
    ]
    organics_data = [
        {"name": "Compost", "nitrogen": 2, "phosphorus": 1, "potassium": 1},
        {"name": "Manure", "nitrogen": 1.5, "phosphorus": 1.2, "potassium": 0.8},
    ]

    inorganic = []
    for f in fertilizers_data:
        if f["nitrogen"] > 0 and deficiency["nitrogen"]:
            amount = (deficiency['nitrogen'] / f['nitrogen']) * 100
            inorganic.append(f"{f['name']} {T['for_nitrogen']}: {amount:.2f} kg")
        if f["phosphorus"] > 0 and deficiency["phosphorus"]:
            amount = (deficiency['phosphorus'] / f['phosphorus']) * 100
            inorganic.append(f"{f['name']} {T['for_phosphorus']}: {amount:.2f} kg")
        if f["potassium"] > 0 and deficiency["potassium"]:
            amount = (deficiency['potassium'] / f['potassium']) * 100
            inorganic.append(f"{f['name']} {T['for_potassium']}: {amount:.2f} kg")

    organic = []
    for f in organics_data:
        if f["nitrogen"] > 0 and deficiency["nitrogen"]:
            amount = (deficiency['nitrogen'] / f['nitrogen']) * 100
            organic.append(f"{f['name']} {T['for_nitrogen']}: {amount:.2f} kg")
        if f["phosphorus"] > 0 and deficiency["phosphorus"]:
            amount = (deficiency['phosphorus'] / f['phosphorus']) * 100
            organic.append(f"{f['name']} {T['for_phosphorus']}: {amount:.2f} kg")
        if f["potassium"] > 0 and deficiency["potassium"]:
            amount = (deficiency['potassium'] / f['potassium']) * 100
            organic.append(f"{f['name']} {T['for_potassium']}: {amount:.2f} kg")

    return inorganic, organic


# 📝 Save result to file
def save_to_file(analysis, inorganic, organic, T):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")
    year_str = now.strftime("%Y")

    result = f"{T['soil_analysis_result']} - {date_str} ({day_str}), {time_str}, {year_str}\n"
    result += f"{T['nutrient_status']}:\n"
    for key, value in analysis.items():
        result += f"{key}: {value}\n"

    result += "\n" + T['inorganic_recommendation'] + ":\n"
    result += "\n".join(inorganic)

    result += "\n\n" + T['organic_recommendation'] + ":\n"
    result += "\n".join(organic)

    with open("soil_analysis_result.txt", "w") as file:
        file.write(result)
