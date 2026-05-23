import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# DATASET YÜKLEME
# ==========================================

CSV_PATH = "global_hantavirus_surveillance_dataset_2026.csv"

if not os.path.exists(CSV_PATH):
    print(f"HATA: {CSV_PATH} bulunamadı!")
    exit()

print("Dataset yükleniyor...")

df = pd.read_csv(CSV_PATH)

print("Dataset başarıyla yüklendi.")
print("Toplam veri:", len(df))

# ==========================================
# GEREKSİZ KOLONLARI SİL
# ==========================================

columns_to_drop = [
    "case_id",
    "report_date",
    "symptoms",
    "recovery_days"
]

existing_cols = [col for col in columns_to_drop if col in df.columns]

df.drop(columns=existing_cols, inplace=True)

# ==========================================
# EKSİK VERİLER
# ==========================================

df.dropna(inplace=True)

print("Eksik veriler temizlendi.")

# ==========================================
# KATEGORİK VERİLERİ ENCODE ET
# ==========================================

label_encoders = {}

categorical_columns = [
    "country",
    "region",
    "virus_strain",
    "transmission_type",
    "exposure_source",
    "gender",
    "hospitalization"
]

for col in categorical_columns:

    if col in df.columns:

        encoder = LabelEncoder()

        df[col] = encoder.fit_transform(
            df[col].astype(str)
        )

        label_encoders[col] = encoder

print("Kategorik veriler encode edildi.")

# ==========================================
# TARGET BELİRLE
# ==========================================

if "fatality" not in df.columns:

    print("HATA: fatality kolonu bulunamadı!")
    exit()

fatality_encoder = LabelEncoder()

df["fatality"] = fatality_encoder.fit_transform(
    df["fatality"].astype(str)
)

# X ve Y
X = df.drop(columns=["fatality"])
y = df["fatality"]

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Train/Test ayrımı tamamlandı.")

# ==========================================
# MODEL
# ==========================================

print("Model eğitiliyor...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

print("Model eğitildi.")

# ==========================================
# TEST SONUÇLARI
# ==========================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL SONUÇLARI")
print("==============================")

print(f"Accuracy: %{round(accuracy * 100, 2)}")

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# ==========================================
# MODEL KAYDET
# ==========================================

joblib.dump(model, "hantavirus_model.pkl")

joblib.dump(label_encoders, "label_encoders.pkl")

print("\nModel başarıyla kaydedildi!")
print("Dosya: hantavirus_model.pkl")

print("\nLabel encoder dosyası oluşturuldu.")
print("Dosya: label_encoders.pkl")
