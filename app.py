import os
import sqlite3
import pickle
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hantavirus-proje-2026'

# ==================== VERİTABANI BAĞLANTISI ====================
def init_db():
    conn = sqlite3.connect('hantavirus.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, region TEXT, risk_score REAL, status TEXT, prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS case_statistics (id INTEGER PRIMARY KEY AUTOINCREMENT, region TEXT, confirmed_cases INTEGER, deaths INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, region TEXT, message TEXT, is_active BOOLEAN DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# ==================== MODEL YÜKLEME ====================
def load_model():
    if os.path.exists('hantavirus_model.pk1'):
        with open('hantavirus_model.pk1', 'rb') as f:
            return pickle.load(f)
    return None

model = load_model()

# ==================== HABER API SERVİSİ ====================
def fetch_news():
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key: return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {'q': 'hantavirus', 'language': 'en', 'apiKey': api_key, 'pageSize': 5}
        response = requests.get(url, params=params, timeout=5)
        return response.json().get('articles', []) if response.status_code == 200 else []
    except:
        return []

# ==================== ROTALAR (SAYFALAR) ====================
@app.route('/')
def index():
    return render_template('index.html', news=fetch_news())

@app.route('/harita')
def harita():
    return render_template('harita.html')

@app.route('/pano')
def pano():
    return render_template('pano.html')

@app.route('/risk-degerlendirmesi')
def risk_degerlendirmesi():
    return render_template('risk_degerlendirmesi.html')

@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')

# ==================== API ENDPOINTS ====================
@app.route('/api/news', methods=['GET'])
def get_news():
    return jsonify({"success": True, "news": fetch_news()})

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # ML modelin yoksa şimdilik sabit bir skor döndürelim
    return jsonify({"success": True, "risk_score": 75, "status": "Yüksek"})

if __name__ == '__main__':
    # Hata ayıklama modunu aç ki hata alırsan nedenini görelim
    app.run(debug=True)
