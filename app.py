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
            st.stop()  # Stop if database connection failed
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
            soils = [("Black Soil",), ("Laterite Soil",), ("Red Soil",), 
                    ("Alluvial Soil",), ("Clay Soil",), ("Sandy Soil",), ("Loamy Soil",)]
            cursor.executemany("INSERT INTO soiltypes (soil_name) VALUES (?)", soils)

        # Insert initial data into crops
        cursor.execute("SELECT COUNT(*) FROM crops")
        if cursor.fetchone()[0] == 0:
            crops = [
                ("Rice", 1), ("Cotton", 1), ("Sugarcane", 1),  # Black Soil
                ("Tea", 2), ("Coffee", 2), ("Rubber", 2),      # Laterite Soil
                ("Groundnut", 3), ("Millets", 3), ("Tobacco", 3),    # Red Soil
                ("Wheat", 4), ("Rice", 4), ("Sugarcane", 4),      # Alluvial Soil
                ("Paddy", 5), ("Jute", 5), ("Wheat", 5),            # Clay Soil
                ("Coconut", 6), ("Groundnut", 6), ("Maize", 6),    # Sandy Soil
                ("Wheat", 7), ("Cotton", 7), ("Vegetables", 7)     # Loamy Soil
            ]
            cursor.executemany("INSERT INTO crops (crop_name, soil_id) VALUES (?, ?)", crops)

        conn.commit()
        conn.close()

# 🔗 Connect to SQLite
def connect_db():
    """Connects to the SQLite database."""
    try:
        conn = sqlite3.connect('soil_recommendation.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Check if the database file exists, and if not, run the setup
if not os.path.exists('soil_recommendation.db'):
    setup_db()
    st.sidebar.success("Database created and initial data loaded.")

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

# 📝 Save result
def save_to_file(analysis, inorganic, organic, T):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")
    year_str = now.strftime("%Y")

    result = f"{T['soil_analysis_result']} - {date_str} ({day_str}), {time_str}, {year_str}\n"
    result += f"{T['nutrient_status']}:\n"
    for key, val in analysis.items():
        result += f"{key}: {val}\n"
    result += f"\n{T['inorganic_fertilizers']}:\n" + "\n".join(inorganic) + "\n"
    result += f"\n{T['organic_fertilizers']}:\n" + "\n".join(organic) + "\n"
    return result

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
        "user_created": "User created.",
        "username_exists": "Username may already exist.",
        "select_soil": "Select Soil Type",
        "select_crop": "Select Crop",
        "nitrogen": "Nitrogen (kg/acre)",
        "phosphorus": "Phosphorus (kg/acre)",
        "potassium": "Potassium (kg/acre)",
        "analyze": "Analyze & Recommend",
        "nutrient_status": "Nutrient Status",
        "inorganic_fertilizers": "Inorganic Fertilizers",
        "organic_fertilizers": "Organic Fertilizers",
        "download_result": "Download Result as .txt file",
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
    "kn": {
        "title": "🌱 ಸ್ಮಾರ್ಟ್ ಮಣ್ಣು ಮತ್ತು ರಸಗೊಬ್ಬರ ಶಿಫಾರಸು ವ್ಯವಸ್ಥೆ",
        "login": "ಲಾಗಿನ್",
        "register": "ನೋಂದಣಿ",
        "username": "ಬಳಕೆದಾರಹೆಸರು",
        "password": "ಪಾಸ್ವರ್ಡ್",
        "new_username": "ಹೊಸ ಬಳಕೆದಾರಹೆಸರು",
        "new_password": "ಹೊಸ ಪಾಸ್ವರ್ಡ್",
        "create_account": "ಖಾತೆ ರಚಿಸಿ",
        "welcome": "ಸ್ವಾಗತ",
        "invalid_credentials": "ಅಮಾನ್ಯವಾದ ವಿವರಗಳು",
        "user_created": "ಬಳಕೆದಾರ ರಚಿಸಲಾಗಿದೆ.",
        "username_exists": "ಬಳಕೆದಾರಹೆಸರು ಈಗಾಗಲೇ ಅಸ್ತಿತ್ವದಲ್ಲಿದೆ.",
        "select_soil": "ಮಣ್ಣಿನ ಪ್ರಕಾರ ಆಯ್ಕೆಮಾಡಿ",
        "select_crop": "ಬೆಳೆಯ ಆಯ್ಕೆಮಾಡಿ",
        "nitrogen": "ಸಾರಜನಕ (ಕೆಜಿ/ಎಕರೆ)",
        "phosphorus": "ರಂಜಕ (ಕೆಜಿ/ಎಕರೆ)",
        "potassium": "ಪೊಟ್ಯಾಸಿಯಮ್ (ಕೆಜಿ/ಎಕರೆ)",
        "analyze": "ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಶಿಫಾರಸು ನೀಡಿ",
        "nutrient_status": "ಪೋಷಕಾಂಶ ಸ್ಥಿತಿ",
        "inorganic_fertilizers": "ಅಕಾರ್ಬನಿಕ ರಸಗೊಬ್ಬರಗಳು",
        "organic_fertilizers": "ಸಸ್ಯಜ ರಸಗೊಬ್ಬರಗಳು",
        "download_result": "ಫಲಿತಾಂಶವನ್ನು .txt ಕಡತವಾಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        "language": "ಭಾಷೆ",
        "soil_analysis_result": "ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ ಫಲಿತಾಂಶ",
        "excess_by": "ಹೆಚ್ಚುವರಿ:",
        "deficient_by": "ಕೊರತೆ:",
        "balanced": "ಸಮತೋಲಿತ",
        "for_nitrogen": "ಸಾರಜನಕಕ್ಕೆ",
        "for_phosphorus": "ರಂಜಕಕ್ಕೆ",
        "for_potassium": "ಪೊಟ್ಯಾಸಿಯಮ್ಗೆ",
        "reset": "ಮರುಹೊಂದಿಸಿ",
    },
    "hi": {
        "title": "🌱 स्मार्ट मृदा और उर्वरक सिफारिश प्रणाली",
        "login": "लॉगिन",
        "register": "रजिस्टर",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "new_username": "नया उपयोगकर्ता नाम",
        "new_password": "नया पासवर्ड",
        "create_account": "खाता बनाएं",
        "welcome": "स्वागत है",
        "invalid_credentials": "अमान्य प्रमाण-पत्र",
        "user_created": "उपयोगकर्ता बनाया गया।",
        "username_exists": "उपयोगकर्ता नाम पहले से मौजूद है।",
        "select_soil": "मृदा प्रकार चुनें",
        "select_crop": "फसल चुनें",
        "nitrogen": "नाइट्रोजन (किग्रा/एकड़)",
        "phosphorus": "फॉस्फोरस (किग्रा/एकड़)",
        "potassium": "पोटेशियम (किग्रा/एकड़)",
        "analyze": "विश्लेषण करें और सिफारिश करें",
        "nutrient_status": "पोषक तत्व स्थिति",
        "inorganic_fertilizers": "अकार्बनिक उर्वरक",
        "organic_fertilizers": "जैविक उर्वरक",
        "download_result": ".txt फ़ाइल के रूप में परिणाम डाउनलोड करें",
        "language": "भाषा",
        "soil_analysis_result": "मृदा विश्लेषण परिणाम",
        "excess_by": "से अधिक",
        "deficient_by": "से कम",
        "balanced": "संतुलित",
        "for_nitrogen": "नाइट्रोजन के लिए",
        "for_phosphorus": "फॉस्फोरस के लिए",
        "for_potassium": "पोटेशियम के लिए",
        "reset": "रीसेट",
    }
}

# 🌿 Streamlit UI
lang = st.sidebar.selectbox("Language / ಭಾಷೆ / भाषा", ["en", "kn", "hi"])
T = translations[lang]

st.title(T["title"])

# Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'analysis_performed' not in st.session_state:
    st.session_state.analysis_performed = False

menu = st.sidebar.selectbox(T["language"], [T["login"], T["register"]])

if menu == T["register"]:
    st.sidebar.subheader(T["create_account"])
    new_uname = st.sidebar.text_input(T["new_username"])
    new_pword = st.sidebar.text_input(T["new_password"], type="password")
    if st.sidebar.button(T["register"]):
        if register_user(new_uname, new_pword):
            st.sidebar.success(T["user_created"])

elif menu == T["login"]:
    st.sidebar.subheader(T["login"])
    uname = st.sidebar.text_input(T["username"])
    pword = st.sidebar.text_input(T["password"], type="password")
    if st.sidebar.button(T["login"]):
        if verify_user(uname, pword):
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.success(f"{T['welcome']} {uname}!")
            st.rerun()
        else:
            st.sidebar.error(T["invalid_credentials"])

if st.session_state.logged_in:
    soils = get_soil_types()
    if not soils:
        st.error("Error: Could not retrieve soil types from the database.")
        st.stop()

    soil_names = [s["soil_name"] for s in soils]
    soil_choice = st.selectbox(T["select_soil"], soil_names)

    if soil_choice:
        soil_id = next(s["id"] for s in soils if s["soil_name"] == soil_choice)
        crops = get_crops_by_soil(soil_id)
        if not crops:
            st.error("Error: Could not retrieve crops for the selected soil from the database.")
            st.stop()
        crop_names = [c["crop_name"] for c in crops]
        crop_choice = st.selectbox(T["select_crop"], crop_names)

        if crop_choice:
            crop_id = next(c["id"] for c in crops if c["crop_name"] == crop_choice)
            n = st.number_input(T["nitrogen"], min_value=0)
            p = st.number_input(T["phosphorus"], min_value=0)
            k = st.number_input(T["potassium"], min_value=0)

            col1, col2 = st.columns([1, 1])

            if col1.button(T["analyze"]):
                analysis = analyze_soil(crop_id, n, p, k, T)
                if analysis:
                    st.session_state.analysis_performed = True
                    st.session_state.analysis = analysis
                    st.session_state.inorganic, st.session_state.organic = recommend_fertilizer(crop_id, n, p, k, T)
                    st.rerun()
                else:
                    st.error("Crop ID is invalid. Please select a valid crop.")
            
            if col2.button(T["reset"]):
                st.session_state.analysis_performed = False
                st.rerun()

            if st.session_state.analysis_performed:
                st.subheader(T["nutrient_status"])
                for key, val in st.session_state.analysis.items():
                    st.write(f"{key}: {val}")

                st.subheader(T["inorganic_fertilizers"])
                st.write("\n".join(st.session_state.inorganic))
                st.subheader(T["organic_fertilizers"])
                st.write("\n".join(st.session_state.organic))

                result = save_to_file(st.session_state.analysis, st.session_state.inorganic, st.session_state.organic, T)
                st.download_button(
                    label=T["download_result"],
                    data=result,
                    file_name="soil_analysis_result.txt",
                    mime="text/plain"
                )
