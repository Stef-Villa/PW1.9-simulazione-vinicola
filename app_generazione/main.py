from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app_generazione.init_db import crea_database
from app_generazione.gen_dati import genera_tutti_i_dati
from app_generazione.utils.conf import get_data_folder
import joblib
import os

def main():
    print("Avvio creazione database...")

    # Percorsi corretti
    paths = get_data_folder()
    data_folder_read = paths['read']    # per leggere file inclusi
    data_folder_write = paths['write']  # per scrivere accanto all'EXE

    db_path = os.path.join(data_folder_write, "cantina.db")
    model_path = os.path.join(data_folder_read, "random_forest_model.pkl")

    # Crea cartella se non esiste (dove scriviamo il DB)
    os.makedirs(data_folder_write, exist_ok=True)

    # Elimina il DB se esiste già 
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Database precedente rimosso: {db_path}")

    # Crea engine e session
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    crea_database(engine)
    session = Session(bind=engine)

    # Carica modello
    print("Caricamento modello ML")
    rf_model = joblib.load(model_path)

    # Genera dati
    print("Generazione dei dati in corso")
    genera_tutti_i_dati(session, rf_model)

    print("Database generato e popolato con successo!")
    input("Premi INVIO per uscire")

if __name__ == "__main__":
    main()