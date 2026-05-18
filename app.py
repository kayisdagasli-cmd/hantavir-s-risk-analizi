import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import os
import plotly.graph_objects as go

# Sayfa Ayarları (Premium Koyu Tema Düzeni)
st.set_page_config(page_title="Hantavirüs Risk Simülatörü", page_icon="☣️", layout="wide")

st.title("☣️ Hantavirüs Salgın ve Risk Analizi Simülatörü")
st.markdown("---")

# Yapay Zeka Modellerini Yükleme Fonksiyonu
@st.cache_resource
def load_models():
    if os.path.exists("hantavirus_model.pkl") and os.path.exists("label_encoders.pkl"):
        model = joblib.load("hantavirus_model.pkl")
        encoders = joblib.load("label_encoders.pkl")
        return model, encoders
    return None, None

model, encoders = load_models()

# Sayfayı Tasarım İçin İki Sütuna Bölüyoruz
col1, col2 = st.columns([1, 1])

# SOL SÜTUN: Simülasyon Girdileri (Kontrol Paneli)
with col1:
    st.header("🎛️ Simülasyon Kontrol Paneli")
    
    # Kullanıcı Seçimleri (Dropdown ve Slider'lar)
    country = st.selectbox("Ülke", ["Canada", "Bolivia", "Chile", "Argentina", "Brazil"])
    virus_strain = st.selectbox("Virüs Varyantı (Türü)", ["Sin Nombre", "Seoul", "Puumala", "Andes"])
    transmission_type = st.selectbox("Bulaşma Şekli", ["Rodent-to-Human", "Human-to-Human"])
    exposure_source = st.selectbox("Maruz Kalma Alanı", ["Agricultural Exposure", "Home Infestation", "Rodent Exposure", "Forest Exposure"])
    gender = st.radio("Cinsiyet", ["Male", "Female"])
    hospitalization = st.radio("Hastaneye Yatış Durumu", ["Yes", "No"])
    
    patient_age = st.slider("Hasta Yaşı", 1, 100, 35)
    temperature = st.slider("Ortalama Sıcaklık (°C)", -10, 45, 24)
    humidity = st.slider("Nem Oranı (%)", 0, 100, 55)
    rodent_index = st.slider("Kemirgen Yoğunluk İndeksi (0-10)", 0, 10, 5)

# SAĞ SÜTUN: Canlı Sonuçlar ve Grafik
with col2:
    st.header("📊 Canlı Analitik Çıktılar")
    
    if model is None:
        st.info("💡 Yapay zeka modeli (pkl dosyaları) yükleniyor veya henüz depoda oluşturulmadı. Render'da ilk çalıştırmada train_model.py tetiklenecektir.")
        # Eğer model henüz yoksa simülasyon efekti için örnek bir test skoru gösterelim
        risk_proba = 45.5
    else:
        try:
            # Seçilen metinleri yapay zekanın anlayacağı sayılara güvenli şekilde dönüştürüyoruz
            def safe_transform(encoder_name, value):
                try:
                    return encoders[encoder_name].transform([value])[0]
                except:
                    return 0

            # Modelin beklediği tüm sütun yapısını hazırlıyoruz
            input_data = {
                "country": safe_transform("country", country),
                "region": 0, 
                "virus_strain": safe_transform("virus_strain", virus_strain),
                "transmission_type": safe_transform("transmission_type", transmission_type),
                "exposure_source": safe_transform("exposure_source", exposure_source),
                "patient_age": patient_age,
                "gender": safe_transform("gender", gender),
                "hospitalization": safe_transform("hospitalization", hospitalization),
                "temperature_celsius": temperature,
                "humidity_percent": humidity,
                "rodent_presence_index": rodent_index,
                "quarantine_days": 0,
                "population_density": 1000,
                "air_quality_index": 50
            }
            
            df_input = pd.DataFrame([input_data])
            
            # Yapay zekadan anlık yüzde risk tahmini alıyoruz
            risk_proba = model.predict_proba(df_input)[0][1] * 100
            
        except Exception as e:
            st.error(f"Hesaplama hatası: {e}")
            risk_proba = 0

    # 📈 Premium Gauge (Hız Göstergesi) Grafiği
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_proba,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Hesaplanan Ölümcül Risk Skoru (%)", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#ff4b4b" if risk_proba > 50 else "#f1c40f"},
            'steps' : [
                {'range': [0, 40], 'color': "#2ecc71"},
                {'range': [40, 70], 'color': "#f39c12"},
                {'range': [70, 100], 'color': "#e74c3c"}]}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

# 📰 CANLI HABERLER BÖLÜMÜ (News API)
st.markdown("---")
st.header("📰 Dünyadan Güncel Hantavirüs Gelişmeleri")

# Buraya News API'den aldığın anahtarı (Key) yapıştırabilirsin. 
# Eğer boş kalırsa sistem hata vermez, bilgi notu gösterir.
NEWS_API_KEY = "" 

if NEWS_API_KEY == "":
    st.info("💡 Canlı haber akışını tam entegre görmek için kodun içindeki NEWS_API_KEY alanına News API anahtarınızı ekleyebilirsiniz.")
else:
    url = f"https://newsapi.org/v2/everything?q=hantavirus&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        articles = res.get("articles", [])[:3] # En güncel 3 haberi listele
        if articles:
            h_cols = st.columns(len(articles))
            for idx, art in enumerate(articles):
                with h_cols[idx]:
                    st.subheader(art['title'][:50] + "...")
                    st.write(art['description'][:150] + "..." if art['description'] else "")
                    st.caption(f"Kaynak: {art['source']['name']} | [Habere Git]({art['url']})")
        else:
            st.write("Yakın zamanda Hantavirüs ile ilgili kritik bir haber bulunamadı.")
    except:
        st.error("Haberler şu an canlı çekilemedi, lütfen API anahtarınızı veya bağlantınızı kontrol edin.")
