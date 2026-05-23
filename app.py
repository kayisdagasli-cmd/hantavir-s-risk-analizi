import os
import sqlite3
import pickle
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# =========================
# ENV AYARLARI
# =========================
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hantavirus-proje-2026'

# =========================
# DATABASE
# =========================
DATABASE = "hantavirus.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tahmin kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        gender TEXT,
        fever INTEGER,
        cough INTEGER,
        breath_shortness INTEGER,
        rodent_contact INTEGER,
        humidity REAL,
        temperature REAL,
        risk_score REAL,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Sistem logları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()

# =========================
# MODEL YÜKLEME
# =========================
MODEL_PATH = "hantavirus_model.pkl"

model = None

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as file:
            model = pickle.load(file)
        print("Model başarıyla yüklendi.")
    except Exception as e:
        print("Model yükleme hatası:", e)
else:
    print("Model dosyası bulunamadı.")

# =========================
# NEWS API
# =========================
def fetch_news():
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return []

    try:
        url = "https://newsapi.org/v2/everything"

        params = {
            "q": "hantavirus",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": api_key
        }

        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            return response.json().get("articles", [])

        return []

    except Exception as e:
        print("News API Hatası:", e)
        return []

# =========================
# ANA SAYFALAR
# =========================
@app.route("/")
def index():
    return render_template(
        "index.html",
        news=fetch_news()
    )


@app.route("/risk-degerlendirmesi")
def risk_degerlendirmesi():
    return render_template("risk_degerlendirmesi.html")


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()

    total_predictions = conn.execute(
        "SELECT COUNT(*) as total FROM predictions"
    ).fetchone()["total"]

    recent_predictions = conn.execute("""
        SELECT * FROM predictions
        ORDER BY created_at DESC
        LIMIT 10
    """).fetchall()

    average_risk = conn.execute("""
        SELECT AVG(risk_score) as avg_risk
        FROM predictions
    """).fetchone()["avg_risk"]

    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        recent_predictions=recent_predictions,
        average_risk=round(average_risk or 0, 2)
    )


@app.route("/harita")
def harita():
    return render_template("harita.html")


@app.route("/hakkinda")
def hakkinda():
    return render_template("hakkinda.html")

# =========================
# API - HABERLER
# =========================
@app.route("/api/news")
def api_news():
    return jsonify({
        "success": True,
        "news": fetch_news()
    })

# =========================
# API - TAHMİN
# =========================
@app.route("/api/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        age = int(data.get("age", 0))
        gender = data.get("gender", "Male")

        fever = int(data.get("fever", 0))
        cough = int(data.get("cough", 0))
        breath_shortness = int(data.get("breath_shortness", 0))
        rodent_contact = int(data.get("rodent_contact", 0))

        humidity = float(data.get("humidity", 50))
        temperature = float(data.get("temperature", 25))

        # Gender encode
        gender_encoded = 1 if gender.lower() == "male" else 0

        # Model girdisi
        features = np.array([[
            age,
            gender_encoded,
            fever,
            cough,
            breath_shortness,
            rodent_contact,
            humidity,
            temperature
        ]])

        # =========================
        # MODEL TAHMİNİ
        # =========================
        if model:

            prediction_probability = model.predict_proba(features)[0][1]

            risk_score = round(prediction_probability * 100, 2)

        else:
            # Model yoksa demo skor
            risk_score = np.random.randint(35, 95)

        # =========================
        # RİSK SEVİYESİ
        # =========================
        if risk_score < 40:
            risk_level = "Düşük Risk"

        elif risk_score < 70:
            risk_level = "Orta Risk"

        else:
            risk_level = "Yüksek Risk"

        # =========================
        # DATABASE KAYDI
        # =========================
        conn = get_db_connection()

        conn.execute("""
        INSERT INTO predictions (
            age,
            gender,
            fever,
            cough,
            breath_shortness,
            rodent_contact,
            humidity,
            temperature,
            risk_score,
            risk_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            age,
            gender,
            fever,
            cough,
            breath_shortness,
            rodent_contact,
            humidity,
            temperature,
            risk_score,
            risk_level
        ))

        conn.commit()
        conn.close()

        # =========================
        # RESPONSE
        # =========================
        return jsonify({
            "success": True,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "analysis_time": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================
# API - SON TAHMİNLER
# =========================
@app.route("/api/recent-predictions")
def recent_predictions():

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT *
        FROM predictions
        ORDER BY created_at DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    data = []

    for row in rows:
        data.append({
            "id": row["id"],
            "age": row["age"],
            "gender": row["gender"],
            "risk_score": row["risk_score"],
            "risk_level": row["risk_level"],
            "created_at": row["created_at"]
        })

    return jsonify({
        "success": True,
        "predictions": data
    })

# =========================
# APP RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
