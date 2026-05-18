import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def train():
    csv_path = "global_hantavirus_surveillance_dataset_2026.csv"
    if not os.path.exists(csv_path):
        print(f"Hata: '{csv_path}' dosyası bulunamadı!")
        return

    df = pd.read_csv(csv_path)
    
    columns_to_drop = ['case_id', 'report_date', 'symptoms', 'recovery_days']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    le_dict = {}
    categorical_cols = ['country', 'region', 'virus_strain', 'transmission_type', 'exposure_source', 'gender', 'hospitalization']
    
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            le_dict[col] = le
            
    if 'fatality' in df.columns:
        le_fatality = LabelEncoder()
        df['fatality'] = le_fatality.fit_transform(df['fatality'].astype(str))
        X = df.drop(columns=['fatality'])
        y = df['fatality']
    else:
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    joblib.dump(model, "hantavirus_model.pkl")
    joblib.dump(le_dict, "label_encoders.pkl")
    print("Modeller başarıyla oluşturuldu!")

if __name__ == "__main__":
    train()
