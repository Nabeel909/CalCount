# 🥗 Calories Advisor App

An intelligent calorie and nutrition estimator app built with **Streamlit** and **Gemini 1.5 Flash API** from Google. Just upload a photo of your food, and the app will:
- Detect food items 🥘
- Estimate total calories 🔥
- Assess nutritional value (carbs, fats, fiber, sugar, etc.) 🧪
- Offer a healthiness recommendation ✅❌

---

## 🚀 Demo

![Demo Preview](demo.gif) *(Optional if you want to include a screen recording)*

---

## 🛠️ Features

- 📸 Upload a food image (JPG, JPEG, PNG)
- 🧠 Processed by Gemini 1.5 Flash (Vision)
- 📊 Visual nutrient breakdown
- 📥 Downloadable PDF report
- 🗂 Upload history tracking (optional with SQLite)

---

## 🧪 Tech Stack

- [Streamlit](https://streamlit.io/) – Web app frontend
- [Google Gemini API](https://ai.google.dev/) – Vision & text model
- [Python 3.10+](https://www.python.org/)
- [Pillow](https://pillow.readthedocs.io/) – Image handling
- [dotenv](https://pypi.org/project/python-dotenv/) – Environment variables

---

## 💾 Installation

```bash
git clone https://github.com/yourusername/calories-advisor.git
cd calories-advisor
pip install -r requirements.txt
