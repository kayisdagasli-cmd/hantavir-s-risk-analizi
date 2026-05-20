from flask import Flask, render_template, request, jsonify
import os
import joblib  # Model dosyası yüklemek için

app = Flask(__name__)

# Yapay Zeka Modelini Güvenli Yükleme Alanı
model = None
MODEL_PATH = "hantavirus_model.pkl"  # Model dosyanızın adı farklıysa burayı değiştirin

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("Yapay zeka modeli başarıyla yüklendi.")
    except Exception as e:
        print(f"Model yükleme hatası: {e}")
else:
    print("Model dosyası bulunamadı, sistem yedek ağırlıklı hesaplama moduna geçiyor.")

# --- SAYFA ROTALARI (ROUTES) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_page():
    # Pano (Genel İstatistikler) Ekranı
    return render_template('dashboard.html')

@app.route('/map')
def map_page():
    # 81 İlli Bölgesel Harita Ekranı
    return render_template('map.html')

@app.route('/assessment')
def assessment_page():
    return render_template('assessment.html')

# --- TAHMİN API ROTASI ---

@app.route('/predict', codecs=['utf-8'], methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Veri alınamadı."}), 400

        # Formdan Gelen Genişletilmiş Veriler
        yas = int(data.get('yas', 0))
        cinsiyet = int(data.get('cinsiyet', 0))
        bolge = data.get('bolge', 'Marmara')
        cevre_tipi = data.get('cevre_tipi', 'Kırsal Tarım')

        # Maruziyet Faktörleri
        kirsal_temas = int(data.get('kirsal_temas', 0))
        kemirgen_temas = int(data.get('kemirgen_temas', 0))
        toz_maruziyeti = int(data.get('toz_maruziyeti', 0))
        son_seyahat = int(data.get('son_seyahat', 0))
        bagisiklik = int(data.get('bagisiklik', 0))

        # Belirtiler
        ates = int(data.get('ates', 0))
        kas_agrisi = int(data.get('kas_agrisi', 0))
        bulanti = int(data.get('bulanti', 0))
        nefes_darligi = int(data.get('nefes_darligi', 0))
        bas_agrisi = int(data.get('bas_agrisi', 0))
        yorgunluk = int(data.get('yorgunluk', 0))

        # HESAPLAMA LOGIC: Yapay zeka modeli yüklüyse onu kullan, değilse yedek klinik puanlamayı devreye sok
        if model is not None:
            # Model girdisi sırası (Eğittiğiniz modele göre buradaki özellikleri düzenleyebilirsiniz)
            features = [yas, cinsiyet, kirsal_temas, kemirgen_temas, toz_maruziyeti, son_seyahat, bagisiklik, ates, kas_agrisi, bulanti, nefes_darligi, bas_agrisi, yorgunluk]
            prediction_proba = model.predict_proba([features])[0][1]
            risk_score = round(prediction_proba * 100, 1)
        else:
            # Gelişmiş Yedek Klinik Puanlama Algoritması
            score = 0
            # Kritik Maruziyetler
            if kemirgen_temas: score += 25
            if kirsal_temas: score += 15
            if toz_maruziyeti: score += 10
            if son_seyahat: score += 10
            if bagisiklik: score += 5
            
            # Kritik Belirtiler
            if nefes_darligi: score += 20  # En kritik hantavirüs semptomu
            if ates: score += 15
            if kas_agrisi: score += 10
            if bas_agrisi: score += 5
            if bulanti: score += 5
            if yorgunluk: score += 5
            
            # Yaş ve Çevre Çarpanı
            if cevre_tipi in ["Kırsal Tarım", "Ormanlık"]: score += 5
            
            risk_score = min(score, 100)

        # Risk Seviyesi Belirleme
        if risk_score < 25:
            risk_status = "DÜŞÜK RİSK"
        elif risk_score < 50:
            risk_status = "ORTA RİSK"
        elif risk_score < 75:
            risk_status = "YÜKSEK RİSK"
        else:
            risk_status = "KRİTİK RİSK"

        return jsonify({
            "success": True,
            "risk_score": risk_score,
            "risk_status": risk_status
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
