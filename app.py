import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from db_setup import setup_db

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'inorganic' not in st.session_state:
        st.session_state.inorganic = []
    if 'organic' not in st.session_state:
        st.session_state.organic = []

# Initialize app
init_session_state()

# Database connection
def get_db_connection():
    try:
        conn = initialize_database()
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error("Username already exists")
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        if user and user[2] == hash_password(password):
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.session_state.logged_in = True
            return True
        return False
    finally:
        conn.close()

# Data retrieval
def get_soil_types():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, soil_name FROM soiltypes ORDER BY soil_name")
        return [{"id": row[0], "soil_name": row[1]} for row in cursor.fetchall()]
    finally:
        conn.close()

def get_crops_by_soil(soil_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, crop_name FROM crops WHERE soil_id = ? ORDER BY crop_name",
            (soil_id,)
        )
        return [{"id": row[0], "crop_name": row[1]} for row in cursor.fetchall()]
    finally:
        conn.close()

# Analysis functions
standard_nutrients = {
    1: {"nitrogen": 50, "phosphorus": 30, "potassium": 40},
    2: {"nitrogen": 45, "phosphorus": 25, "potassium": 35},
    3: {"nitrogen": 60, "phosphorus": 40, "potassium": 50},
    4: {"nitrogen": 80, "phosphorus": 60, "potassium": 70},
    5: {"nitrogen": 70, "phosphorus": 55, "potassium": 65},
    6: {"nitrogen": 90, "phosphorus": 75, "potassium": 85},
    7: {"nitrogen": 85, "phosphorus": 70, "potassium": 80},
}

def analyze_soil(crop_id, n, p, k):
    std = standard_nutrients.get(crop_id)
    if not std:
        return None
    return {
        "Nitrogen": f"Excess by {n - std['nitrogen']:.2f}" if n > std["nitrogen"]
        else f"Deficient by {std['nitrogen'] - n:.2f}" if n < std["nitrogen"] else "Balanced",
        "Phosphorus": f"Excess by {p - std['phosphorus']:.2f}" if p > std["phosphorus"]
        else f"Deficient by {std['phosphorus'] - p:.2f}" if p < std["phosphorus"] else "Balanced",
        "Potassium": f"Excess by {k - std['potassium']:.2f}" if k > std["potassium"]
        else f"Deficient by {std['potassium'] - k:.2f}" if k < std["potassium"] else "Balanced"
    }

def recommend_fertilizer(crop_id, n, p, k):
    std = standard_nutrients.get(crop_id)
    if not std:
        return [], []

    deficiency = {
        "nitrogen": max(0, std["nitrogen"] - n),
        "phosphorus": max(0, std["phosphorus"] - p),
        "potassium": max(0, std["potassium"] - k),
    }

    fertilizers = [
        {"name": "Urea", "nitrogen": 46, "phosphorus": 0, "potassium": 0},
        {"name": "DAP", "nitrogen": 18, "phosphorus": 46, "potassium": 0},
        {"name": "MOP", "nitrogen": 0, "phosphorus": 0, "potassium": 60},
    ]
    organics = [
        {"name": "Compost", "nitrogen": 2, "phosphorus": 1, "potassium": 1},
        {"name": "Manure", "nitrogen": 1.5, "phosphorus": 1.2, "potassium": 0.8},
    ]

    inorganic = []
    organic = []
    
    for fert in fertilizers:
        if fert["nitrogen"] > 0 and deficiency["nitrogen"]:
            amount = (deficiency['nitrogen'] / fert['nitrogen']) * 100
            inorganic.append(f"{fert['name']} for Nitrogen: {amount:.2f} kg")
        if fert["phosphorus"] > 0 and deficiency["phosphorus"]:
            amount = (deficiency['phosphorus'] / fert['phosphorus']) * 100
            inorganic.append(f"{fert['name']} for Phosphorus: {amount:.2f} kg")
        if fert["potassium"] > 0 and deficiency["potassium"]:
            amount = (deficiency['potassium'] / fert['potassium']) * 100
            inorganic.append(f"{fert['name']} for Potassium: {amount:.2f} kg")

    for org in organics:
        if org["nitrogen"] > 0 and deficiency["nitrogen"]:
            amount = (deficiency['nitrogen'] / org['nitrogen']) * 100
            organic.append(f"{org['name']} for Nitrogen: {amount:.2f} kg")
        if org["phosphorus"] > 0 and deficiency["phosphorus"]:
            amount = (deficiency['phosphorus'] / org['phosphorus']) * 100
            organic.append(f"{org['name']} for Phosphorus: {amount:.2f} kg")
        if org["potassium"] > 0 and deficiency["potassium"]:
            amount = (deficiency['potassium'] / org['potassium']) * 100
            organic.append(f"{org['name']} for Potassium: {amount:.2f} kg")

    return inorganic, organic

# Main App UI
st.title("🌱 Smart Soil & Fertilizer Recommendation System")

# Authentication
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.sidebar.subheader("Create Account")
    new_user = st.sidebar.text_input("Username")
    new_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Register"):
        if register_user(new_user, new_pass):
            st.sidebar.success("Account created successfully!")

elif menu == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if verify_user(username, password):
            st.success(f"Welcome {username}!")
        else:
            st.sidebar.error("Invalid credentials")

# Main Application
if st.session_state.logged_in:
    try:
        soils = get_soil_types()
        if not soils:
            st.error("No soil types found in database")
            st.stop()

        soil_choice = st.selectbox(
            "Select Soil Type",
            [s["soil_name"] for s in soils]
        )
        soil_id = next(s["id"] for s in soils if s["soil_name"] == soil_choice)
        
        crops = get_crops_by_soil(soil_id)
        if not crops:
            st.error("No crops found for selected soil type")
            st.stop()
        
        crop_choice = st.selectbox(
            "Select Crop",
            [c["crop_name"] for c in crops]
        )
        crop_id = next(c["id"] for c in crops if c["crop_name"] == crop_choice)
        
        st.subheader("Soil Nutrient Levels")
        n = st.number_input("Nitrogen (kg/acre)", min_value=0)
        p = st.number_input("Phosphorus (kg/acre)", min_value=0)
        k = st.number_input("Potassium (kg/acre)", min_value=0)
        
        col1, col2 = st.columns(2)
        if col1.button("Analyze & Recommend"):
            analysis = analyze_soil(crop_id, n, p, k)
            if analysis:
                st.session_state.analysis = analysis
                st.session_state.inorganic, st.session_state.organic = recommend_fertilizer(crop_id, n, p, k)
                st.rerun()
        
        if col2.button("Reset"):
            st.session_state.analysis = None
            st.rerun()
        
        if st.session_state.analysis:
            st.subheader("Analysis Results")
            for nutrient, status in st.session_state.analysis.items():
                st.write(f"{nutrient}: {status}")
            
            st.subheader("Recommended Inorganic Fertilizers")
            for fert in st.session_state.inorganic:
                st.write(fert)
            
            st.subheader("Recommended Organic Fertilizers")
            for fert in st.session_state.organic:
                st.write(fert)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
