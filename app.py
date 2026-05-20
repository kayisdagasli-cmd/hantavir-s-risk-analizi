from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# 1. MODEL YÜKLEME
# Model dosyanızla birebir eşleşen güvenli yükleme alanı
try:
    with open('hantavirüs_model.pk1', 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print(f"Model yükleme hatası: {str(e)}")

# 2. ROTALAR (SAYFA BAĞLANTILARI)

@app.route('/')
def home():
    """Ana Sayfa"""
    return render_template('index.html')

@app.route('/assessment')
def assessment():
    """Risk Değerlendirme Sihirbazı Sayfası (Eksik harfli dosya adınıza eşitlendi)"""
    return render_template('assesment.html')

@app.route('/map')
def map_page():
    """Bölgesel Risk Haritası ve Dashboard Ekranı"""
    return render_template('dashboard.html')

# 3. YAPAY ZEKA TAHMİN MOTORU

@app.route('/predict', methods=['POST'])
def predict():
    """Formdan gelen verileri işleyen ve risk skoru üreten fonksiyon"""
    if model is None:
        return jsonify({'success': False, 'error': 'Yapay zeka modeli sunucuda yüklenemedi.'})
        
    try:
        data = request.json
        
        # Form verilerini modelin beklediği sıraya göre listeye çeviriyoruz
        features = [
            int(data.get('yas', 0)),
            int(data.get('cinsiyet', 0)),
            int(data.get('kirsal_temas', 0)),
            int(data.get('kemirgen_temas', 0)),
            int(data.get('ates', 0)),
            int(data.get('kas_agrisi', 0)),
            int(data.get('bulanti', 0)),
            int(data.get('nefes_darligi', 0))
        ]
        
        # Olasılık tahmini hesaplama
        prediction_proba = model.predict_proba([features])[0][1]
        risk_score = round(prediction_proba * 100, 1)
        
        # Risk seviyesi eşikleri
        if risk_score < 30:
            risk_status = "DÜŞÜK RİSK"
        elif risk_score < 70:
            risk_status = "ORTA RİSK"
        else:
            risk_status = "YÜKSEK RİSK"
            
        return jsonify({
            'success': True,
            'risk_score': risk_score,
            'risk_status': risk_status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
