import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime
from db_setup import setup_db

# 🔗 Connect to SQLite
def connect_db():
    """Connects to the SQLite database."""
    try:
        conn = sqlite3.connect('soil_recommendation.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Check and initialize database
if not os.path.exists('soil_recommendation.db'):
    setup_db()
    st.sidebar.success("Database initialized successfully!")

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
        st.error(T["username_exists"])
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

# 🎯 Standard nutrients (temporary - should be moved to database)
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

# 🌐 Multi-language labels
translations = {
    "en": {
        "title": "🌱 Smart Soil & Fertilizer Recommendation System",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "new_username": "New Username",
        "new_password": "New Password",
        "create_account": "Create Account",
        "welcome": "Welcome",
        "invalid_credentials": "Invalid credentials",
        "user_created": "User created successfully!",
        "username_exists": "Username already exists",
        "select_soil": "Select Soil Type",
        "select_crop": "Select Crop",
        "nitrogen": "Nitrogen (kg/acre)",
        "phosphorus": "Phosphorus (kg/acre)",
        "potassium": "Potassium (kg/acre)",
        "analyze": "Analyze & Recommend",
        "nutrient_status": "Nutrient Status",
        "inorganic_fertilizers": "Inorganic Fertilizers",
        "organic_fertilizers": "Organic Fertilizers",
        "download_result": "Download Result",
        "language": "Language",
        "soil_analysis_result": "Soil Analysis Result",
        "excess_by": "Excess by",
        "deficient_by": "Deficient by",
        "balanced": "Balanced",
        "for_nitrogen": "for Nitrogen",
        "for_phosphorus": "for Phosphorus",
        "for_potassium": "for Potassium",
        "reset": "Reset",
    },
    # Add other languages as needed...
}

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'analysis_performed' not in st.session_state:
    st.session_state.analysis_performed = False

# UI Setup
lang = st.sidebar.selectbox("Language", ["en"])
T = translations[lang]
st.title(T["title"])

# Authentication
menu = st.sidebar.selectbox("Menu", [T["login"], T["register"]])

if menu == T["register"]:
    st.sidebar.subheader(T["create_account"])
    new_user = st.sidebar.text_input(T["new_username"])
    new_pass = st.sidebar.text_input(T["new_password"], type="password")
    if st.sidebar.button(T["register"]):
        if register_user(new_user, new_pass):
            st.sidebar.success(T["user_created"])

elif menu == T["login"]:
    st.sidebar.subheader(T["login"])
    username = st.sidebar.text_input(T["username"])
    password = st.sidebar.text_input(T["password"], type="password")
    if st.sidebar.button(T["login"]):
        if verify_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"{T['welcome']} {username}!")
        else:
            st.sidebar.error(T["invalid_credentials"])

# Main Application
if st.session_state.logged_in:
    soils = get_soil_types()
    if not soils:
        st.error("Could not load soil data. Please check database connection.")
        st.stop()

    soil_choice = st.selectbox(T["select_soil"], [s["soil_name"] for s in soils])
    soil_id = next(s["id"] for s in soils if s["soil_name"] == soil_choice)
    
    crops = get_crops_by_soil(soil_id)
    if not crops:
        st.error("No crops found for selected soil type.")
        st.stop()
    
    crop_choice = st.selectbox(T["select_crop"], [c["crop_name"] for c in crops])
    crop_id = next(c["id"] for c in crops if c["crop_name"] == crop_choice)
    
    n = st.number_input(T["nitrogen"], min_value=0)
    p = st.number_input(T["phosphorus"], min_value=0)
    k = st.number_input(T["potassium"], min_value=0)
    
    col1, col2 = st.columns(2)
    if col1.button(T["analyze"]):
        analysis = analyze_soil(crop_id, n, p, k, T)
        if analysis:
            st.session_state.analysis = analysis
            st.session_state.inorganic, st.session_state.organic = recommend_fertilizer(crop_id, n, p, k, T)
            st.session_state.analysis_performed = True
    
    if col2.button(T["reset"]):
        st.session_state.analysis_performed = False
        st.rerun()
    
    if st.session_state.analysis_performed:
        st.subheader(T["nutrient_status"])
        for nutrient, status in st.session_state.analysis.items():
            st.write(f"{nutrient}: {status}")
        
        st.subheader(T["inorganic_fertilizers"])
        for fert in st.session_state.inorganic:
            st.write(fert)
        
        st.subheader(T["organic_fertilizers"])
        for fert in st.session_state.organic:
            st.write(fert)
        
        # Download functionality would go here
