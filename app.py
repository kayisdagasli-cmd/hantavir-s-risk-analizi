from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import requests
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hantavirus-risk-analysis-2024'

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('hantavirus.db')
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        temperature REAL,
        humidity REAL,
        rainfall REAL,
        rodent_population REAL,
        risk_score REAL,
        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'normal'
    )
    ''')
    
    # Alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        risk_level TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Case statistics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS case_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        confirmed_cases INTEGER DEFAULT 0,
        suspected_cases INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0,
        recovery_rate REAL DEFAULT 0.0,
        report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ==================== MODEL LOADING ====================
def load_model():
    try:
        with open('hantavirus_model.pk1', 'rb') as f:
            model = pickle.load(f)
        return model
    except:
        return None

model = load_model()

# ==================== NEWS API INTEGRATION ====================
def fetch_news():
    """Haberlerden güncel bilgileri çek"""
    try:
        api_key = os.getenv('NEWS_API_KEY', '')
        if not api_key:
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'hantavirus',
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': api_key,
            'pageSize': 5
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get('articles', [])
    except:
        pass
    
    return []

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Ana Sayfa"""
    conn = sqlite3.connect('hantavirus.db')
    cursor = conn.cursor()
    
    # Son vaka istatistikleri
    cursor.execute('SELECT SUM(confirmed_cases), SUM(deaths) FROM case_statistics')
    total_cases, total_deaths = cursor.fetchone()
    
    # Aktif uyarılar
    cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_active=1')
    active_alerts = cursor.fetchone()[0]
    
    conn.close()
    
    news = fetch_news()
    
    return render_template('index.html', 
                         total_cases=total_cases or 0,
                         total_deaths=total_deaths or 0,
                         active_alerts=active_alerts)

@app.route('/harita')
def harita():
    """Harita Sayfası"""
    return render_template('harita.html')

@app.route('/pano')
def pano():
    """Dashboard Sayfası"""
    conn = sqlite3.connect('hantavirus.db')
    cursor = conn.cursor()
    
    # Son tahminler
    cursor.execute('''
    SELECT region, risk_score, status, prediction_date 
    FROM predictions 
    ORDER BY prediction_date DESC LIMIT 10
    ''')
    predictions = cursor.fetchall()
    
    # Bölge dağılımı
    cursor.execute('''
    SELECT region, confirmed_cases 
    FROM case_statistics 
    ORDER BY confirmed_cases DESC
    ''')
    regional_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('pano.html', 
                         predictions=predictions,
                         regional_data=regional_data)

@app.route('/risk-degerlendirmesi')
def risk_degerlendirmesi():
    """Risk Değerlendirme Sayfası"""
    return render_template('risk_degerlendirmesi.html')

@app.route('/hakkinda')
def hakkinda():
    """Hakkında Sayfası"""
    return render_template('hakkinda.html')

@app.route('/hantavirus-nedir')
def hantavirus_nedir():
    """Hantavirus Bilgi Sayfası"""
    return render_template('hantavirus_nedir.html')

@app.route('/gosterge-paneli')
def gosterge_paneli():
    """Gösterge Paneli (Admin Dashboard)"""
    return render_template('gosterge_paneli.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Risk Tahmini - ML Modelini Kullan"""
    try:
        data = request.get_json()
        
        # Veri hazırlama
        features = np.array([[
            float(data.get('temperature', 20)),
            float(data.get('humidity', 50)),
            float(data.get('rainfall', 100)),
            float(data.get('rodent_population', 50))
        ]])
        
        # Model tahmini
        if model:
            risk_score = model.predict(features)[0]
        else:
            # Model yoksa formül kullan
            risk_score = calculate_risk(data)
        
        risk_score = float(risk_score)
        status = determine_risk_status(risk_score)
        region = data.get('region', 'Unknown')
        
        # Veritabanına kaydet
        conn = sqlite3.connect('hantavirus.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO predictions (region, temperature, humidity, rainfall, rodent_population, risk_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (region, data.get('temperature'), data.get('humidity'), 
              data.get('rainfall'), data.get('rodent_population'), risk_score, status))
        conn.commit()
        
        # Uyarı oluştur (gerekirse)
        if risk_score > 70:
            cursor.execute('''
            INSERT INTO alerts (region, risk_level, message, is_active)
            VALUES (?, ?, ?, 1)
            ''', (region, status, f"{region} bölgesinde yüksek risk tespit edildi!"))
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'risk_score': risk_score,
            'status': status,
            'message': f"Risk Skoru: {risk_score:.2f}"
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Vaka İstatistikleri"""
    try:
        conn = sqlite3.connect('hantavirus.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM case_statistics')
        stats = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except:
        return jsonify({'success': False}), 400

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Aktif Uyarılar"""
    try:
        conn = sqlite3.connect('hantavirus.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, region, risk_level, message, created_at 
        FROM alerts 
        WHERE is_active=1 
        ORDER BY created_at DESC
        ''')
        alerts = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
    except:
        return jsonify({'success': False}), 400

@app.route('/api/news', methods=['GET'])
def get_news():
    """Güncel Haberler"""
    try:
        news = fetch_news()
        return jsonify({
            'success': True,
            'news': news
        })
    except:
        return jsonify({'success': False}), 400

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Yönetici Paneli Verileri"""
    try:
        conn = sqlite3.connect('hantavirus.db')
        cursor = conn.cursor()
        
        # Toplam istatistikler
        cursor.execute('SELECT COUNT(*), SUM(confirmed_cases), SUM(deaths) FROM case_statistics')
        total_regions, total_cases, total_deaths = cursor.fetchone()
        
        # Aktif uyarılar
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_active=1')
        active_alerts = cursor.fetchone()[0]
        
        # Son tahminler
        cursor.execute('SELECT region, risk_score, status FROM predictions ORDER BY prediction_date DESC LIMIT 5')
        recent_predictions = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_regions': total_regions or 0,
            'total_cases': total_cases or 0,
            'total_deaths': total_deaths or 0,
            'active_alerts': active_alerts,
            'recent_predictions': recent_predictions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/admin/add-case', methods=['POST'])
def add_case():
    """Yeni Vaka Ekle"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('hantavirus.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO case_statistics (region, confirmed_cases, suspected_cases, deaths, recovery_rate)
        VALUES (?, ?, ?, ?, ?)
        ''', (data.get('region'), data.get('confirmed'), data.get('suspected'), 
              data.get('deaths'), data.get('recovery_rate', 0)))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Vaka başarıyla eklendi'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== HELPER FUNCTIONS ====================

def calculate_risk(data):
    """
    Hantavirus Risk Formülü
    Risk = (Temp * 0.2) + (Humidity * 0.3) + (Rainfall * 0.2) + (Rodent * 0.3)
    """
    temp_factor = float(data.get('temperature', 20)) / 100 * 20
    humidity_factor = float(data.get('humidity', 50)) / 100 * 30
    rainfall_factor = float(data.get('rainfall', 100)) / 200 * 20
    rodent_factor = float(data.get('rodent_population', 50)) / 100 * 30
    
    risk_score = temp_factor + humidity_factor + rainfall_factor + rodent_factor
    return min(100, max(0, risk_score))

def determine_risk_status(score):
    """Risk Seviyesi Belirle"""
    if score < 30:
        return 'düşük'
    elif score < 60:
        return 'orta'
    elif score < 80:
        return 'yüksek'
    else:
        return 'çok_yüksek'

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ==================== RUN ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
