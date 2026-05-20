from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
import requests

app = Flask(__name__)

# Yapay Zeka Modellerini Yükleme Fonksiyonu
def load_models():
    # Render'da model ismi 'hantavirüs_model.pk1' olarak ayarlandığı için ona eşitledim
    model_path = "hantavirüs_model.pk1"
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return model
        except:
            return None
    return None

model = load_models()

# 1. ANA SAYFA ROTASI (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# 2. PANEL / PANO ROTASI (dashboard.html)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 3. RİSK DEĞERLENDİRME SİHİRBAZI ROTASI (assessment.html)
@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

# 4. YAPAY ZEKA TAHMİN / HESAPLAMA ROTASI (API)
@app.route('/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        model = load_models()
        
    data = request.get_json()
    
    try:
        # Eğer yapay zeka modeli yüklüyse gerçek tahmini yap
        if model is not None:
            # JavaScript'ten gelen verileri modelin beklediği formata sokuyoruz
            input_features = [
                int(data.get('rodent_contact', 0)),
                int(data.get('outdoor_activity', 0)),
                int(data.get('dust_exposure', 0)),
                int(data.get('fever', 0)),
                int(data.get('headache', 0)),
                int(data.get('fatigue', 0)),
                int(data.get('muscle_pain', 0)),
                int(data.get('nausea', 0)),
                int(data.get('dyspnea', 0))
            ]
            
            # Örnek hesaplama algoritması (Model yapına göre)
            df_input = np.array([input_features])
            
            # Eğer model predict_proba destekliyorsa olasılık al, yoksa predict et
            if hasattr(model, "predict_proba"):
                risk_score = int(model.predict_proba(df_input)[0][1] * 100)
            else:
                # Model tahmini 1 ise yüksek skor, 0 ise dinamik skor ata
                pred = model.predict(df_input)[0]
                risk_score = 85 if pred == 1 else 25
        else:
            # Model yüklenene kadar sistemin çökmemesi için dinamik simülasyon skoru
            base_score = 10
            if data.get('rodent_contact') == 1: base_score += 25
            if data.get('fever') == 1: base_score += 20
            if data.get('dyspnea') == 1: base_score += 25
            if data.get('dust_exposure') == 1: base_score += 10
            risk_score = min(base_score, 100)

        # Risk Seviyesini Belirleme
        if risk_score >= 70:
            risk_level = "YÜKSEK"
            suggestions = [
                "Acil olarak bir sağlık kuruluşuna başvurun.",
                "Kendinizi izole edin ve başkalarıyla temasınızı minimize edin.",
                "Kapalı alanlarda N95 maske kullanın.",
                "Yüksek riskli açık alanlarda koruyucu giysi giyin."
            ]
        elif risk_score >= 40:
            risk_level = "ORTA"
            suggestions = [
                "Belirtilerinizi yakından takip edin, ateşinizi düzenli ölçün.",
                "Bir hekime danışarak durum hakkında bilgi verin.",
                "Kemirgenlerin bulunabileceği alanlardan uzak durun.",
                "Bulunduğunuz kapalı alanları sık sık havalandırın."
            ]
        else:
            risk_level = "DÜŞÜK"
            suggestions = [
                "Genel hijyen kurallarına uymaya devam edin.",
                "Düzenli el yıkama ve kişisel hijyen önlemlerine devam edin.",
                "Yaşam alanlarınızda kemirgen kontrolü sağlayın."
            ]

        return jsonify({
            'risk_score': risk_score,
            'risk_level': risk_level,
            'suggestions': suggestions
        })

    except Exception as e:
        return jsonify({'error': str(e), 'risk_score': 0, 'risk_level': 'HATA', 'suggestions': ['Hesaplama yapılamadı.']}), 400

if __name__ == '__main__':
    app.run(debug=True)
