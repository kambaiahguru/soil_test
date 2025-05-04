import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from db_setup import setup_db
import pandas as pd
from io import StringIO

# Language mapping
language_options = ["English", "Hindi", "Kannada"]
language_map = {
    "English": {
        "menu": "Menu",
        "login": "Login",
        "register": "Register",
        "create_account": "Create Account",
        "username": "Username",
        "password": "Password",
        "register_button": "Register",
        "login_button": "Login",
        "invalid_credentials": "Invalid credentials",
        "welcome": "Welcome",
        "soil_type": "Select Soil Type",
        "no_soil_found": "No soil types found in database",
        "crop": "Select Crop",
        "no_crop_found": "No crops found for selected soil type",
        "nutrient_levels": "Soil Nutrient Levels",
        "nitrogen": "Nitrogen (kg/acre)",
        "phosphorus": "Phosphorus (kg/acre)",
        "potassium": "Potassium (kg/acre)",
        "analyze_recommend": "Analyze & Recommend",
        "reset": "Reset",
        "analysis_results": "Analysis Results",
        "recommended_inorganic": "Recommended Inorganic Fertilizers",
        "recommended_organic": "Recommended Organic Fertilizers",
        "download_results": "Download Results",
        "excess_by": "Excess by",
        "deficient_by": "Deficient by",
        "balanced": "Balanced",
        "no_nutrient_data": "No standard nutrient data found for this crop.",
        "crop_determination_failed": "Could not determine the selected crop.",
        "download_file_name": "soil_analysis_results",
        "register_exists": "already exists",
    },
    "Hindi": {
        "menu": "मेनू",
        "login": "लॉगिन",
        "register": "रजिस्टर",
        "create_account": "खाता बनाएँ",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "register_button": "रजिस्टर करें",
        "login_button": "लॉगिन करें",
        "invalid_credentials": "अमान्य क्रेडेंशियल",
        "welcome": "स्वागत है",
        "soil_type": "मिट्टी का प्रकार चुनें",
        "no_soil_found": "डेटाबेस में कोई मिट्टी का प्रकार नहीं मिला",
        "crop": "फसल चुनें",
        "no_crop_found": "चयनित मिट्टी के प्रकार के लिए कोई फसल नहीं मिली",
        "nutrient_levels": "मिट्टी पोषक तत्व स्तर",
        "nitrogen": "नाइट्रोजन (किलोग्राम/एकड़)",
        "phosphorus": "फास्फोरस (किलोग्राम/एकड़)",
        "potassium": "पोटेशियम (किलोग्राम/एकड़)",
        "analyze_recommend": "विश्लेषण और सिफारिश करें",
        "reset": "रीसेट",
        "analysis_results": "विश्लेषण परिणाम",
        "recommended_inorganic": "अनुशंसित अकार्बनिक उर्वरक",
        "recommended_organic": "अनुशंसित कार्बनिक उर्वरक",
        "download_results": "परिणाम डाउनलोड करें",
        "excess_by": "से अधिक",
        "deficient_by": "से कम",
        "balanced": "संतुलित",
        "no_nutrient_data": "इस फसल के लिए कोई मानक पोषक तत्व डेटा नहीं मिला।",
        "crop_determination_failed": "चयनित फसल का निर्धारण नहीं किया जा सका।",
        "download_file_name": "मृदा_विश्लेषण_परिणाम",
        "register_exists": "पहले से मौजूद है",
    },
    "Kannada": {
        "menu": "ಮೆನು",
        "login": "ಲಾಗ್ ಇನ್",
        "register": "ನೋಂದಾಯಿಸಿ",
        "create_account": "ಖಾತೆ ರಚಿಸಿ",
        "username": "ಬಳಕೆದಾರ ಹೆಸರು",
        "password": "ಗುಪ್ತಪದ",
        "register_button": "ನೋಂದಾಯಿಸಿ",
        "login_button": "ಲಾಗ್ ಇನ್",
        "invalid_credentials": "ಅಮಾನ್ಯ ರುಜುವಾತುಗಳು",
        "welcome": "ಸ್ವಾಗತ",
        "soil_type": "ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
        "no_soil_found": "ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಯಾವುದೇ ಮಣ್ಣಿನ ಪ್ರಕಾರಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        "crop": "ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಿ",
        "no_crop_found": "ಆಯ್ಕೆ ಮಾಡಿದ ಮಣ್ಣಿನ ಪ್ರಕಾರಕ್ಕೆ ಯಾವುದೇ ಬೆಳೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        "nutrient_levels": "ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ ಮಟ್ಟಗಳು",
        "nitrogen": "ಸಾರಜನಕ (ಕೆಜಿ/ಎಕರೆ)",
        "phosphorus": "ರಂಜಕ (ಕೆಜಿ/ಎಕರೆ)",
        "potassium": "ಪೊಟ್ಯಾಸಿಯಮ್ (ಕೆಜಿ/ಎಕರೆ)",
        "analyze_recommend": "ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಶಿಫಾರಸು ಮಾಡಿ",
        "reset": "ಮರುಹೊಂದಿಸಿ",
        "analysis_results": "ವಿಶ್ಲೇಷಣೆ ಫಲಿತಾಂಶಗಳು",
        "recommended_inorganic": "ಶಿಫಾರಸು ಮಾಡಲಾದ ಅಜೈವಿಕ ಗೊಬ್ಬರಗಳು",
        "recommended_organic": "ಶಿಫಾರಸು ಮಾಡಲಾದ ಸಾವಯವ ಗೊಬ್ಬರಗಳು",
        "download_results": "ಫಲಿತಾಂಶಗಳನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        "excess_by": "ಇಂದ ಹೆಚ್ಚುವರಿ",
        "deficient_by": "ಇಂದ ಕೊರತೆ",
        "balanced": "ಸಮತೋಲಿತ",
        "no_nutrient_data": "ಈ ಬೆಳೆಗೆ ಯಾವುದೇ ಪ್ರಮಾಣಿತ ಪೋಷಕಾಂಶ ದತ್ತಾಂಶ ಕಂಡುಬಂದಿಲ್ಲ.",
        "crop_determination_failed": "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆಯನ್ನು ನಿರ್ಧರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        "download_file_name": "ಮಣ್ಣಿನ_ವಿಶ್ಲೇಷಣೆ_ಫಲಿತಾಂಶಗಳು",
        "register_exists": "ಈಗಾಗಲೇ ಅಸ್ತಿತ್ವದಲ್ಲಿದೆ",
    },
}

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
    if 'language' not in st.session_state:
        st.session_state.language = "English"

# Initialize app
init_session_state()

# Language selection
selected_language = st.sidebar.selectbox("Language / भाषा / ಭಾಷೆ", language_options)
st.session_state.language = selected_language
lang = language_map[st.session_state.language]

# Database connection
def get_db_connection():
    try:
        conn = setup_db()
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
        st.error(lang["username"] + " " + lang["register_exists"])
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
standard_nutrients_list = [
    {"nitrogen": 50, "phosphorus": 30, "potassium": 40},
    {"nitrogen": 45, "phosphorus": 25, "potassium": 35},
    {"nitrogen": 60, "phosphorus": 40, "potassium": 50},
    {"nitrogen": 45, "phosphorus": 25, "potassium": 35},
    {"nitrogen": 50, "phosphorus": 30, "potassium": 40},
    {"nitrogen": 55, "phosphorus": 35, "potassium": 45},
    {"nitrogen": 60, "phosphorus": 40, "potassium": 50},
    {"nitrogen": 50, "phosphorus": 30, "potassium": 40},
    {"nitrogen": 70, "phosphorus": 50, "potassium": 60},
    {"nitrogen": 80, "phosphorus": 60, "potassium": 70},
    {"nitrogen": 75, "phosphorus": 55, "potassium": 65},
    {"nitrogen": 85, "phosphorus": 65, "potassium": 75},
    {"nitrogen": 70, "phosphorus": 50, "potassium": 60},
    {"nitrogen": 65, "phosphorus": 45, "potassium": 55},
    {"nitrogen": 80, "phosphorus": 60, "potassium": 70},
    {"nitrogen": 90, "phosphorus": 70, "potassium": 80},
    {"nitrogen": 60, "phosphorus": 40, "potassium": 50},
    {"nitrogen": 75, "phosphorus": 55, "potassium": 65},
    {"nitrogen": 85, "phosphorus": 65, "potassium": 75},
    {"nitrogen": 70, "phosphorus": 50, "potassium": 60},
    {"nitrogen": 80, "phosphorus": 60, "potassium": 70},
]

def analyze_soil(crop_index, n, p, k):
    if 0 <= crop_index < len(standard_nutrients_list):
        std = standard_nutrients_list[crop_index]
        return {
            "Nitrogen": f"{lang['excess_by']} {n - std['nitrogen']:.2f}" if n > std["nitrogen"]
            else f"{lang['deficient_by']} {std['nitrogen'] - n:.2f}" if n < std["nitrogen"] else lang["balanced"],
            "Phosphorus": f"{lang['excess_by']} {p - std['phosphorus']:.2f}" if p > std["phosphorus"]
            else f"{lang['deficient_by']} {std['phosphorus'] - p:.2f}" if p < std["phosphorus"] else lang["balanced"],
            "Potassium": f"{lang['excess_by']} {k - std['potassium']:.2f}" if k > std["potassium"]
            else f"{lang['deficient_by']} {std['potassium'] - k:.2f}" if k < std["potassium"] else lang["balanced"]
        }
    return None

def recommend_fertilizer(crop_index, n, p, k):
    if 0 <= crop_index < len(standard_nutrients_list):
        std = standard_nutrients_list[crop_index]
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
    return [], []

def download_results(analysis_results, inorganic_recommendations, organic_recommendations):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    day = now.strftime("%A")
    year = now.strftime("%Y")

    results_text = f"Soil Analysis and Fertilizer Recommendation\n"
    results_text += f"Date: {now.strftime('%Y-%m-%d')}\n"
    results_text += f"Time: {now.strftime('%H:%M:%S')}\n"
    results_text += f"Day: {day}\n"
    results_text += f"Year: {year}\n\n"
    results_text += "Analysis Results:\n"
    if analysis_results:
        for nutrient, status in analysis_results.items():
            results_text += f"- {nutrient}: {status}\n"
    else:
        results_text += "No analysis performed.\n"

    results_text += "\nRecommended Inorganic Fertilizers:\n"
    if inorganic_recommendations:
        for recommendation in inorganic_recommendations:
            results_text += f"- {recommendation}\n"
    else:
        results_text += "No inorganic fertilizer recommendations.\n"

    results_text += "\nRecommended Organic Fertilizers:\n"
    if organic_recommendations:
        for recommendation in organic_recommendations:
            results_text += f"- {recommendation}\n"
    else:
        results_text += "No organic fertilizer recommendations.\n"

    return results_text

# Main App UI
st.title("🌱 Smart Soil & Fertilizer Recommendation System")

# Authentication
menu = st.sidebar.selectbox(lang["menu"], [lang["login"], lang["register"]])

if menu == lang["register"]:
    st.sidebar.subheader(lang["create_account"])
    new_user = st.sidebar.text_input(lang["username"])
    new_pass = st.sidebar.text_input(lang["password"], type="password")
    if st.sidebar.button(lang["register_button"]):
        if register_user(new_user, new_pass):
            st.sidebar.success("Account created successfully!")

elif menu == lang["login"]:
    st.sidebar.subheader(lang["login"])
    username = st.sidebar.text_input(lang["username"])
    password = st.sidebar.text_input(lang["password"], type="password")
    if st.sidebar.button(lang["login_button"]):
        if verify_user(username, password):
            st.success(f"{lang['welcome']} {username}!")
        else:
            st.sidebar.error(lang["invalid_credentials"])

# Main Application
if st.session_state.logged_in:
    try:
        soils = get_soil_types()
        if not soils:
            st.error(lang["no_soil_found"])
            st.stop()

        soil_choice = st.selectbox(
            lang["soil_type"],
            [s["soil_name"] for s in soils]
        )
        soil_id = next(s["id"] for s in soils if s["soil_name"] == soil_choice)

        crops_data = get_crops_by_soil(soil_id)
        if not crops_data:
            st.error(lang["no_crop_found"])
            st.stop()

        crop_names = [c["crop_name"] for c in crops_data]
        crop_choice = st.selectbox(
            lang["crop"],
            crop_names
        )
        try:
            crop_index = crop_names.index(crop_choice)
        except ValueError:
            crop_index = -1

        st.subheader(lang["nutrient_levels"])
        n = st.number_input(lang["nitrogen"], min_value=0)
        p = st.number_input(lang["phosphorus"], min_value=0)
        k = st.number_input(lang["potassium"], min_value=0)

        col1, col2, col3 = st.columns(3)
        if col1.button(lang["analyze_recommend"]):
            if crop_index != -1:
                analysis = analyze_soil(crop_index, n, p, k)
                if analysis:
                    st.session_state.analysis = analysis
                    st.session_state.inorganic, st.session_state.organic = recommend_fertilizer(crop_index, n, p, k)
                    st.rerun()
                else:
                    st.warning(lang["no_nutrient_data"])
            else:
                st.error(lang["crop_determination_failed"])

        if col2.button(lang["reset"]):
            st.session_state.analysis = None
            st.session_state.inorganic = []
            st.session_state.organic = []
            st.rerun()

        if st.session_state.analysis:
            st.subheader(lang["analysis_results"])
            for nutrient, status in st.session_state.analysis.items():
                st.write(f"{nutrient}: {status}")

            st.subheader(lang["recommended_inorganic"])
            for fert in st.session_state.inorganic:
                st.write(fert)

            st.subheader(lang["recommended_organic"])
            for fert in st.session_state.organic:
                st.write(fert)
            
            if col3.button(lang["download_results"]):
                results_text = download_results(st.session_state.analysis, st.session_state.inorganic, st.session_state.organic)
                st.download_button(
                    label="Download",
                    data=results_text.encode('utf-8'),
                    file_name=f"{lang['download_file_name']}.txt",
                    mime="text/plain",
                )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
