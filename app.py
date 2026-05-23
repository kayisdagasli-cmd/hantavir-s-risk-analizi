import os
import sqlite3
import pickle
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .env dosyasından anahtarları yükle
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hantavirus-risk-analysis-2024'

# ==================== VERİTABANI İNİT ====================
def init_db():
    conn = sqlite3.connect('hantavirus.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY, region TEXT, risk_score REAL, status TEXT, prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS case_statistics (id INTEGER PRIMARY KEY, region TEXT, confirmed_cases INTEGER, deaths INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, region TEXT, risk_level TEXT, message TEXT, is_active BOOLEAN DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# ==================== HABER API (GÜNCEL) ====================
def fetch_news():
    try:
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key: return []
        url = "https://newsapi.org/v2/everything"
        params = {'q': 'hantavirus', 'sortBy': 'publishedAt', 'language': 'en', 'apiKey': api_key, 'pageSize': 5}
        response = requests.get(url, params=params, timeout=5)
        return response.json().get('articles', []) if response.status_code == 200 else []
    except:
        return []

# ==================== ROTALAR ====================
@app.route('/')
def index():
    # Haberleri çek
    news = fetch_news()
    return render_template('index.html', news=news)

@app.route('/pano')
def pano():
    return render_template('pano.html')

@app.route('/harita')
def harita():
    return render_template('harita.html')

@app.route('/risk-degerlendirmesi', methods=['GET', 'POST'])
def risk_degerlendirmesi():
    if request.method == 'POST':
        # Buraya formdan gelen verilerle ML tahmin kodu gelecek
        return jsonify({"message": "Analiz tamamlandı"})
    return render_template('risk_degerlendirmesi.html')

@app.route('/api/news', methods=['GET'])
def get_news_api():
    return jsonify({"success": True, "news": fetch_news()})

if __name__ == '__main__':
    app.run(debug=True)
