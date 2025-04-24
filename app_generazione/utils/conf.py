import os
import sys

# Dizionario per inflazione storica
inflazione_storica = {
    2019: 0.006,
    2020: -0.002,
    2021: 0.019,
    2022: 0.081,
    2023: 0.057,
    2024: 0.016
}

def get_data_folder():
    if getattr(sys, 'frozen', False):
        # Base path per lettura da EXE
        base_path = sys._MEIPASS
        # Percorso dove scrivere il DB (accanto all'EXE)
        write_path = os.path.dirname(sys.executable)
    else:
        # Base path per sviluppo
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        write_path = base_path

    return {
        'read': os.path.join(base_path, "data"),
        'write': os.path.join(write_path, "data")
    }