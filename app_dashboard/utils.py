from sqlalchemy import text
import pandas as pd
from app_dashboard.db import SessionLocal

def get_magazzino(anno="all"):
    session = SessionLocal()
    if anno == "all":
        query = text("""
            SELECT anno, tipo_vino, bottiglie_disp, prezzo
            FROM magazzino
            WHERE bottiglie_disp > 0
            ORDER BY anno, tipo_vino
        """)
        result = session.execute(query).fetchall()
    else:
        query = text("""
            SELECT anno, tipo_vino, bottiglie_disp, prezzo
            FROM magazzino
            WHERE anno = :anno AND bottiglie_disp > 0
            ORDER BY tipo_vino
        """)
        result = session.execute(query, {"anno": anno}).fetchall()
    session.close()   
    return pd.DataFrame(result, columns=["Anno", "Tipo Vino", "Bottiglie", "Prezzo"])


def get_dipendenti():
    session = SessionLocal()
    query = text("""
        SELECT nome, ruolo, stipendio_annuo
        FROM dipendenti
        ORDER BY ruolo
    """)
    result = session.execute(query).fetchall()
    session.close()
    return pd.DataFrame(result, columns=["Nome", "Ruolo", "Stipendio"])


def get_ultime_vendite(n=10):
    session = SessionLocal()
    query = text("""
        SELECT data, tipo_vino, canale_vendita, quantità_venduta, incasso
        FROM vendite
        ORDER BY data DESC
        LIMIT :n
    """)
    result = session.execute(query, {"n": n}).fetchall()
    session.close()
    return pd.DataFrame(result, columns=["Data", "Tipo Vino", "Canale", "Quantità", "Incasso"])
