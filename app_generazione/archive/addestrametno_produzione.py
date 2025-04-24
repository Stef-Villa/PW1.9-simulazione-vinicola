from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pandas as pd
import joblib 

# Caricare il file CSV per visualizzare i dati
file_path = r'data\csv_dati_reali_produzione_meteo_piemonte.csv'
df = pd.read_csv(file_path, sep=';')

# Mostrare le prime righe per verificare la corretta lettura del file
print(df.head())

# Calcolare la produzione per ettaro
df['produzione_per_ettaro'] = df['produzione_uva_quintali'] / df['superficie_ettari']

# Funzione per eseguire la Random Forest sulla produzione per ettaro
def random_forest_produzione_ettaro(df):
    # Selezioniamo le variabili indipendenti (features) e la variabile dipendente (target)
    X = df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']]
    y = df['produzione_per_ettaro']
    
    # Creiamo il modello Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Addestriamo il modello sui dati
    model.fit(X, y)
    
    # Restituiamo il modello addestrato
    return model

# Eseguiamo il modello di Random Forest sui dati
rf_model = random_forest_produzione_ettaro(df)

# Fare le previsioni con il modello addestrato
y_pred_rf = rf_model.predict(df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']])

# Calcolare R² e RMSE per il modello Random Forest
r2_rf = r2_score(df['produzione_per_ettaro'], y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(df['produzione_per_ettaro'], y_pred_rf))

joblib.dump(rf_model, 'random_forest_model.pkl')

print("R² (Random Forest):", r2_rf)
print("RMSE (Random Forest):", rmse_rf)