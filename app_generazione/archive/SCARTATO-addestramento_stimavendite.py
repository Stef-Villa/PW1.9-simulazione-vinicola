# import pandas as pd
# from sklearn.linear_model import LinearRegression
# import joblib

# # Caricamento CSV
# file_path = "dati\dataset_ml_vendite.csv"  
# df = pd.read_csv(file_path, sep=';')

# # Selezione colonne da usare
# df.columns = df.columns.str.strip().str.lower()
# df['produzione_bottiglie'] = df['produzione_bottiglie'].astype(float)
# df['inflazione'] = df['inflazione'].astype(float)
# df['consumo_bottiglie'] = df['consumo_bottiglie'].astype(float)

# # Definizione feature e target
# X = df[['produzione_bottiglie', 'inflazione']]
# y = df['consumo_bottiglie']

# # Addestramento modello
# model = LinearRegression()
# model.fit(X, y)

# # Calcolo coefficienti e R²
# coeffs = dict(zip(X.columns, model.coef_))
# intercept = model.intercept_
# r_squared = model.score(X, y)

# print("\n=== MODELLO ADDDESTRATO ===")
# print("Coefficiente produzione_bottiglie:", coeffs['produzione_bottiglie'])
# print("Coefficiente inflazione:", coeffs['inflazione'])
# print("Intercetta:", intercept)
# print("R² (R-quadro):", r_squared)

# # Salvataggio modello con joblib
# output_path = "modello_ml_vendite_noscaler.pkl"
# joblib.dump(model, output_path)
# print("\nModello salvato")

# # import pandas as pd
# # from sklearn.ensemble import RandomForestRegressor
# # from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
# # import joblib

# # # Caricamento del CSV aggiornato
# # df = pd.read_csv("dati\dataset_ml_vendite.csv", sep=";")

# # # Separazione delle feature e del target
# # X = df[["produzione_bottiglie", "inflazione"]]
# # y = df["consumo_bottiglie"]

# # # Addestramento del modello
# # modello_rf = RandomForestRegressor(random_state=42, n_estimators=100)
# # modello_rf.fit(X, y)

# # # Valutazione del modello
# # y_pred = modello_rf.predict(X)
# # r2 = r2_score(y, y_pred)
# # mse = mean_squared_error(y, y_pred)

# # # Salvataggio del modello
# # joblib.dump(modello_rf, "modello_rf_vendite.pkl")

# # # === Predizione sui dati di addestramento ===
# # predizioni = modello_rf.predict(X)

# # # === Valutazione del modello ===
# # mae = mean_absolute_error(y, predizioni)
# # r2 = r2_score(y, predizioni)

# # print(f"MAE: {mae:.2f}")
# # print(f"R²: {r2:.3f}")