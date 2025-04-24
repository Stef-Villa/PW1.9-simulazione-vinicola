# from sklearn.linear_model import LinearRegression
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_squared_error, r2_score
# import numpy as np
# import pandas as pd

# # Caricare il file CSV per visualizzare i dati
# file_path = r'C:\Users\Stefano\Desktop\simulazione-vino\dati\csv_dati_reali_produzione_meteo_piemonte.csv'
# df = pd.read_csv(file_path, sep=';')

# # Mostrare le prime righe per verificare la corretta lettura del file
# print(df.head())

# # Calcolare la produzione per ettaro
# df['produzione_per_ettaro'] = df['produzione_uva_quintali'] / df['superficie_ettari']

# # Funzione per eseguire la regressione lineare sulla produzione per ettaro
# def regressione_lineare_produzione_ettaro(df):
#     # Selezioniamo le variabili indipendenti (features) e la variabile dipendente (target)
#     X = df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']]
#     y = df['produzione_per_ettaro']
    
#     # Creiamo il modello di regressione lineare
#     model = LinearRegression()
    
#     # Addestriamo il modello sui dati
#     model.fit(X, y)
    
#     # Restituiamo il modello addestrato, i coefficienti e l'intercetta
#     return model, model.coef_, model.intercept_

# # Eseguiamo la regressione lineare sulla produzione per ettaro
# model, coefficients, intercept = regressione_lineare_produzione_ettaro(df)

# # Fare le previsioni con il modello addestrato
# y_pred = model.predict(df[['temp_media', 'umidita_media', 'pioggia_mm', 'vento_kmh']])

# # Calcolare R² e RMSE
# r2 = r2_score(df['produzione_per_ettaro'], y_pred)
# rmse = np.sqrt(mean_squared_error(df['produzione_per_ettaro'], y_pred))

# print("R²:", r2)
# print("RMSE:", rmse)

# # Stampare i coefficienti per riferimenti
# print("Coefficiente per la temperatura media:", coefficients[0])
# print("Coefficiente per l'umidità media:", coefficients[1])
# print("Coefficiente per la pioggia (mm):", coefficients[2])
# print("Coefficiente per la velocità del vento (km/h):", coefficients[3])
# print("Intercetta:", intercept)