from dash import Dash
from app_dashboard.callbacks import register_callbacks
import webbrowser
import threading
from app_dashboard.layout_main import layout
import pandas as pd
from flask import send_file
import io
import sqlite3
import socket


app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "La Mia Cantina"
app.layout = layout

# Registra tutti i callback in un file separato
register_callbacks(app)

# Apertura automatica nel browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Download CSV Ambiente
@app.server.route("/scarica-csv")
def scarica_csv():
    # Connessione diretta al DB
    conn = sqlite3.connect("data/cantina.db")

    # Legge tutta la tabella Ambiente
    query = "SELECT * FROM Ambiente"
    df = pd.read_sql_query(query, conn)

    # Chiudi connessione
    conn.close()

    # Salva il CSV in memoria
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Ritorna il file come download
    return send_file(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="dati_ambiente.csv"
    )

if __name__ == "__main__":
    if is_port_in_use(8050):
        open_browser()
    else:
        threading.Timer(1.0, open_browser).start()
        app.run(debug=False)