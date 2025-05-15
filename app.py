import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import sqlite3
import pandas as pd
import io
from fpdf import FPDF
from streamlit_lottie import st_lottie
import requests

# -------------------- SETUP --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_Key"))

# -------------------- DB SETUP --------------------
conn = sqlite3.connect('upload_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history
             (filename TEXT, response TEXT)''')
conn.commit()

# -------------------- FUNCTIONS --------------------
def input_image_setup(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return [{
        "mime_type": uploaded_file.type,
        "data": bytes_data
    }]

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def extract_nutrition_data(response_text):
    nutrients = ["Carbohydrates", "Fats", "Fibers", "Sugar"]
    data = {}
    for line in response_text.split("\n"):
        for nutrient in nutrients:
            if nutrient.lower() in line.lower():
                try:
                    value = int(''.join(filter(str.isdigit, line)))
                    data[nutrient] = value
                except:
                    continue
    return data

def generate_bar_chart(data_dict):
    df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['%'])
    st.subheader("📊 Nutrient Breakdown")
    st.bar_chart(df)

def save_to_db(filename, response):
    c.execute("INSERT INTO history (filename, response) VALUES (?, ?)", (filename, response))
    conn.commit()

def generate_pdf_report(filename, response_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Calories Advisor Report", ln=True, align='C')
    pdf.ln(10)

    # Filename and Gemini Response
    pdf.multi_cell(0, 10, txt=f"Filename: {filename}\n\nResponse:\n{response_text}")
    pdf.ln(10)

    # Nutrition Table
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt="Extracted Nutrition Breakdown", ln=True)
    pdf.set_font("Arial", size=12)
    nutrition_data = extract_nutrition_data(response_text)
    if nutrition_data:
        col_width = 50
        row_height = 10
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(col_width, row_height, "Nutrient", 1, 0, 'C', True)
        pdf.cell(col_width, row_height, "Percentage", 1, 1, 'C', True)

        for nutrient, value in nutrition_data.items():
            pdf.cell(col_width, row_height, nutrient, 1)
            pdf.cell(col_width, row_height, f"{value}%", 1, 1)
    else:
        pdf.cell(0, 10, "No nutrition data extracted.", ln=True)

    # Return BytesIO PDF
    pdf_output = pdf.output(dest='S').encode('latin1')
    return io.BytesIO(pdf_output)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# -------------------- UI --------------------
st.set_page_config(page_title="🍽️ Calories Advisor", layout="centered", page_icon="🥗")

# -------------------- Custom CSS --------------------
st.markdown("""
<style>
body {
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: white;
}
.app-container {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    max-width: 850px;
    margin: auto;
    color: #fff;
}
h1 {
    color: #4CAF50;
    font-family: 'Arial', sans-serif;
    text-align: center;
}
div.stButton > button:first-child {
    background-color: #00C853;
    color: white;
    border-radius: 30px;
    font-size: 18px;
    padding: 0.75em 2em;
    margin-top: 10px;
    transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: #00E676;
    color: black;
}
footer {
    color: #00C853;
    font-size: 14px;
    font-family: 'Arial', sans-serif;
}
footer .stLink {
    color: #00C853;
    text-decoration: underline;
}
.info-box {
    margin-top: 40px;
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(135deg, #333333 0%, #444444 100%);
    color: #f0f0f0;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease;
    font-family: 'Segoe UI', sans-serif;
}
.info-box:hover {
    transform: translateY(-5px);
}
.info-box h4 {
    margin-bottom: 0.3em;
    font-size: 1.4em;
    color: #ffffff;
}
.info-box p {
    margin: 6px 0;
    font-size: 1.05em;
    color: #f0f0f0;
}
.info-box a {
    color: #ffffff;
    text-decoration: none;
    font-weight: bold;
}
.info-box a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.title("Options")
    theme_mode = st.radio("Choose Theme", ["Light", "Dark"])
    if st.button("🗂 View Upload History"):
        with st.expander("📜 Previous Responses"):
            rows = c.execute("SELECT * FROM history ORDER BY ROWID DESC LIMIT 5").fetchall()
            for r in rows:
                st.write(f"🖼 {r[0]}:\n\n{r[1]}\n---")

if theme_mode == "Dark":
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

# -------------------- Main Container --------------------
st.markdown('<div class="app-container">', unsafe_allow_html=True)

st.markdown("<h1>🍽️ Calories Advisor App</h1>", unsafe_allow_html=True)

# Animation
lottie_food = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_hdy0htc4.json")
if lottie_food:
    st_lottie(lottie_food, height=250, key="calorieLottie")

st.write("👋 Upload a food image and get a nutritional breakdown with calorie info.")

# File upload
uploaded_file = st.file_uploader("📸 Upload your food image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(Image.open(uploaded_file), caption="📷 Uploaded Image", use_column_width=True)
    filename = uploaded_file.name

    input_prompt = """
    You are an expert nutritionist. Based on the food image, identify the items and estimate total calories. 
    Format:
    1. Item 1 - No. of calories
    2. Item 2 - No. of calories
    ...

    Finally, mention if the food is healthy or not, and provide the percentage split of carbohydrates, fats, 
    fibers, sugar, and other important nutrients.
    """

    if st.button("🧠 Analyze Calories"):
        with st.spinner("🧬 Processing..."):
            try:
                image_data = input_image_setup(uploaded_file)
                response = get_gemini_response(input_prompt, image_data)
                st.subheader("🧠 Expert's Advise")
                st.success(response)

                save_to_db(filename, response)

                # Chart
                nutrition_data = extract_nutrition_data(response)
                if nutrition_data:
                    generate_bar_chart(nutrition_data)

                # PDF
                pdf_buffer = generate_pdf_report(filename, response)
                st.download_button("📥 Download PDF Report", pdf_buffer, file_name="calorie_report.pdf")

            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Info Section --------------------
st.markdown("""
<div class="info-box">
    <h4>👨‍💻 Nabeel Imran</h4>
    <p>🚀 Turning food into facts, one pixel at a time</p>
    <p>📧 <strong>Email:</strong> imrannabeel654@gmail.com</p>
    <p>🔗 <a href="https://www.linkedin.com/in/nabeel-imran-b58252209/" target="_blank">LinkedIn Profile</a></p>
</div>
""", unsafe_allow_html=True)
