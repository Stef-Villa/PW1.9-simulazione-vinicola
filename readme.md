PROGETTO - Report annuale di un’azienda vinicola 
SimulazIone dati ambientali, produzione e vendita
PW 1.9 | Corso di laurea Informatica per le aziende digitali | A.A. 2024-2025
Università Telematica Pegaso

Questo progetto consiste nella simulazione e visualizzazione delle attività di un'azienda vitivinicola tramite un database generato artificialmente e una dashboard interattiva realizzata in Python.

ISTRUZIONI PER UTENTE FINALE:
    - Necessario installazione di Python 3.10 (python.org)
    - Aprire il terminale
    - Spostarsi in cartella progetto con comando cd
    - Eseguire comendo: pip install -r requirements.txt
    - Per generare nuovo database con dati simulati doppio click su file exe GeneraCantinaDB.exe (non richiede Python)
    - Per avviare dashboard doppio click su file avvia_dashboard.bat (se server Dash già attivo verrà aperto automaticamente il browser)


OBIETTIVI: 
    - Simulare dati realistici per un’azienda agricola nel settore vinicolo
    - Creare una dashboard interattiva per analizzare dati ambientali, produttivi, finanziari e di vendita

TECNOLOGIE USATE:
    - Python 3.10 (ambiente conda)
    - Dash & Plotly – per la visualizzazione interattiva
    - Pandas, NumPy – per la gestione e trasformazione dei dati
    - SQLAlchemy – per l'interfaccia col database SQLite
    - scikit-learn, joblib – per l’utilizzo del modello ML preaddestrato

Genera database
    app_generazione/main.py

Avvia dashboard
    app_dashboard/app.py


FUNZIONALITÀ DASHBOARD
    Visualizzazione vendite, incassi, margini e marketing
    Indicatori ambientali annuali e stagionali
    Analisi della produzione e magazzino
    Tabelle interattive e filtri per anno
    Esportazione dati in CSV

DATI SIMULATI
    Produzione: simulata fino all’anno 2024 (ultima annata vinificata)
    Vendite: simulate giorno per giorno fino alla data odierna del 2025
    Dati ambientali: generati fino alla data attuale (es. 21 aprile 2025)
    La dashboard è predisposta per aggiornarsi ogni 60 secondi con dcc.Interval, ma non include una simulazione incrementale, in quanto non richiesta dalla traccia


Autore
Villa Stefano 
Matricola UniPegaso: 0312200803


