from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pandas as pd
import joblib 

# file CSV con dati sotrici
file_path = r'data\csv_dati_reali_produzione_meteo_piemonte.csv'
df = pd.read_csv(file_path, sep=';')

print(df.head())

# Calcolo produzione per ettaro
df['produzione_per_ettaro'] = df['produzione_uva_quintali'] / df['superficie_ettari']

# Random Forest sulla produzione per ettaro
def random_forest_produzione_ettaro(df):
    # ariabili indipendenti e la variabile dipendente 
    X = df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']]
    y = df['produzione_per_ettaro']
    
    # Creazione modello Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Addestriamento
    model.fit(X, y)
    
    return model

# Esecuzione modello sui dati
rf_model = random_forest_produzione_ettaro(df)

# previsioni con il modello addestrato
y_pred_rf = rf_model.predict(df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']])

# R² e RMSE del modello
r2_rf = r2_score(df['produzione_per_ettaro'], y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(df['produzione_per_ettaro'], y_pred_rf))

joblib.dump(rf_model, 'random_forest_model.pkl')

print("R² (Random Forest):", r2_rf)
print("RMSE (Random Forest):", rmse_rf)
