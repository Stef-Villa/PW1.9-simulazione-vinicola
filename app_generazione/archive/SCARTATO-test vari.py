# from sqlalchemy import create_engine, func
# from sqlalchemy.orm import Session
# from models import Vendite
# import pandas as pd

# engine = create_engine("sqlite:///cantina.db")
# session = Session(bind=engine)

# vendite_per_anno = (
#     session.query(func.strftime("%Y", Vendite.data), func.sum(Vendite.quantità_venduta))
#     .group_by(func.strftime("%Y", Vendite.data))
#     .all()
# )

# df_vendite = pd.DataFrame(vendite_per_anno, columns=["Anno", "Totale Bottiglie Vendute"])
# df_vendite["Anno"] = df_vendite["Anno"].astype(int)
# df_vendite = df_vendite.sort_values(by="Anno")

# print(df_vendite)

# session.close()

# import joblib
# import pandas as pd

# # Carica il modello ML salvato
# modello = joblib.load("modello_ml_vendite_noscaler.pkl")

# # Estrae i coefficienti se il modello è una regressione lineare
# coefficienti = modello.coef_
# print(f"Tipo di modello: {type(modello)}")

# # Stampa i coefficienti
# coefficienti = modello.coef_

# # Definisci i nomi delle feature (nell'ordine corretto usato per l'addestramento)
# nomi_feature = ["produzione_bottiglie", "inflazione"]

# # Mostra i coefficienti in DataFrame
# df = pd.DataFrame({
#     "Variabile": nomi_feature,
#     "Coefficiente": coefficienti
# })

# print(df)