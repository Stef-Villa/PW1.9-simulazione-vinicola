from app_dashboard.utils import get_magazzino, get_dipendenti, get_ultime_vendite
from dash import Input, Output, State, dash_table, callback_context, html
from sqlalchemy import text
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app_dashboard.db import SessionLocal
from flask import request


# Carica CSV per il confronto mercato vs cantina
df_mercato = pd.read_csv("data/dataset_ml_vendite.csv", sep=";")
df_mercato = df_mercato[df_mercato["anno"] >= 2019]
df_mercato["anno"] = df_mercato["anno"].astype(int)

def register_callbacks(app):

    # Dropdown anni per grafici
    @app.callback(
        Output("dropdown-anno", "options"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_opzioni_dropdown(_):
        session = SessionLocal()
        query = text("SELECT DISTINCT strftime('%Y', data) AS anno FROM vendite ORDER BY anno")
        result = session.execute(query).fetchall()
        session.close()
        anni = [{"label": "Tutti gli anni", "value": "all"}] + [{"label": str(r[0]), "value": str(r[0])} for r in result]
        return anni

    # Grafico: vendite annuali
    @app.callback(
        Output("grafico-vendite-annuali", "figure"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_vendite_annuali(_):
        session = SessionLocal()
        query = text("""
            SELECT strftime('%Y', data) AS anno, SUM(quantità_venduta) AS bottiglie
            FROM vendite
            GROUP BY anno
            ORDER BY anno
        """)
        result = session.execute(query).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Anno", "Bottiglie"])
        fig = px.bar(df, x="Anno", y="Bottiglie", title="BOTTIGLIE VENDUTE", text="Bottiglie")
        fig.update_traces(texttemplate="%{text:,}", textposition="inside", insidetextanchor="middle")
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return fig

    # Grafico: incassi annuali
    @app.callback(
        Output("grafico-incassi-annuali", "figure"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_incassi_annuali(_):
        session = SessionLocal()
        query = text("""
            SELECT strftime('%Y', data) AS anno, SUM(incasso) AS totale
            FROM vendite GROUP BY anno ORDER BY anno
        """)
        result = session.execute(query).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Anno", "Incasso"])

        if df.empty:
            return px.line(title="Nessun dato disponibile per gli incassi annuali", template="plotly")

        # Forza template e tipo colonne
        df["Anno"] = df["Anno"].astype(str)
        df["Incasso"] = df["Incasso"].astype(float)

        fig = px.line(
            df,
            x="Anno",
            y="Incasso",
            markers=True,
            title="INCASSO",
            
        )
        return fig

    # Grafico: margini
    @app.callback(
        Output("grafico-margini-annuali", "figure"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_margini(_):
        session = SessionLocal()
        query = text("""
            SELECT
                v.anno,
                v.incasso_totale,
                c.costi_totali,
                v.incasso_totale - c.costi_totali AS margine
            FROM (
                SELECT strftime('%Y', data) AS anno, SUM(incasso) AS incasso_totale
                FROM vendite GROUP BY anno
            ) v
            LEFT JOIN (
                SELECT anno,
                       (ammortamento + investimento_marketing + costo_personale +
                       (costo_materiali_per_bottiglia * totale_bottiglie)) AS costi_totali
                FROM (
                    SELECT *,
                        (SELECT SUM(quantità_venduta)
                         FROM vendite WHERE strftime('%Y', data) = c.anno) AS totale_bottiglie
                    FROM costi_annui c
                )
            ) c ON v.anno = c.anno
            ORDER BY v.anno
        """)
        result = session.execute(query).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Anno", "Ricavi", "Costi", "Margine"])
        fig = px.bar(
            df,
            x="Anno",
            y="Margine",
            title="UTILE",
            color="Margine",
            color_continuous_scale=["red", "orange", "green"],
            text="Margine"
        )

        fig.update_traces(
            texttemplate="€ %{text:,.0f}",
            textposition="inside",
            insidetextanchor="middle"
        )

        fig.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            yaxis_title="Margine (€)"
        )
        return fig
    
    # Grafico vendite mensili
    @app.callback(
        Output("grafico-vendite-mensili", "figure"),
        Input("dropdown-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_vendite_mensili(anno, _):
        session = SessionLocal()

        if anno == "all":
            # Media per mese calcolata su tutti gli anni disponibili
            query = text("""
                SELECT
                    strftime('%m', data) AS mese,
                    SUM(quantità_venduta) / COUNT(DISTINCT strftime('%Y', data)) AS media
                FROM vendite
                GROUP BY mese
                ORDER BY mese
            """)
            result = session.execute(query).fetchall()
            titolo = "VENDITE PER MESE - MEDIA"
        else:
            query = text("""
                SELECT
                    strftime('%m', data) AS mese,
                    SUM(quantità_venduta) AS totale
                FROM vendite
                WHERE strftime('%Y', data) = :anno
                GROUP BY mese
                ORDER BY mese
            """)
            result = session.execute(query, {"anno": anno}).fetchall()
            titolo = f"VENDITE PER MESE - {anno}"

        session.close()

        df = pd.DataFrame(result, columns=["Mese", "Media"])
        mappa_mesi = {
            "01": "Gen", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "Mag", "06": "Giu", "07": "Lug", "08": "Ago",
            "09": "Set", "10": "Ott", "11": "Nov", "12": "Dic"
        }
        df["Mese"] = df["Mese"].map(mappa_mesi)

        fig = px.line(
            df,
            x="Mese",
            y="Media",
            markers=True,
            line_shape="spline",
            title=titolo
        )
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            xaxis_title="Mese",
            yaxis_title="Bottiglie vendute (media)",
            hovermode="x unified"
        )

        return fig
    
    # Grafico torta tripartizione tipo vino
    @app.callback(
        Output("grafico-ripartizione-vini", "figure"),
        Input("dropdown-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_torta_vini(anno, _):
        session = SessionLocal()

        if anno == "all":
            # Media percentuale per tipo vino su tutti gli anni
            query = text("""
                SELECT tipo_vino, SUM(quantità_venduta) AS totale
                FROM vendite
                GROUP BY tipo_vino
            """)
            titolo = "TIPOLOGIA VINO - MEDIA"
        else:
            query = text("""
                SELECT tipo_vino, SUM(quantità_venduta) AS totale
                FROM vendite
                WHERE strftime('%Y', data) = :anno
                GROUP BY tipo_vino
            """)
            titolo = f"TIPOLOGIA VINO - {anno}"

        result = session.execute(query, {"anno": anno} if anno != "all" else {}).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Tipo", "Vendite"])
        fig = px.pie(
            df,
            names="Tipo",
            values="Vendite",
            title=titolo,
            hole=0.4
        )
        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="%{label}<br>%{value} bottiglie<br>%{percent}",
            pull=[0.02] * len(df)  # leggero distacco
        )
        return fig

    # Grafico: ripartizione canali vendita
    @app.callback(
        Output("grafico-canali", "figure"),
        Input("dropdown-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_torta_canali(anno, _):
        session = SessionLocal()

        if anno == "all":
            query = text("""
                SELECT canale_vendita, SUM(quantità_venduta) AS totale
                FROM vendite
                GROUP BY canale_vendita
            """)
            titolo = "CANALE VENDITE - MEDIA"
        else:
            query = text("""
                SELECT canale_vendita, SUM(quantità_venduta) AS totale
                FROM vendite
                WHERE strftime('%Y', data) = :anno
                GROUP BY canale_vendita
            """)
            titolo = f"CANALE VENDITE - {anno}"

        result = session.execute(query, {"anno": anno} if anno != "all" else {}).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Canale", "Vendite"])

        colori = {
            "cantina": "#8e44ad",
            "online": "#2980b9",
            "negozio/ristorante": "#27ae60",
            "export": "#e67e22"
        }

        fig = px.pie(
            df,
            names="Canale",
            values="Vendite",
            title=titolo,
            hole=0.3,  # piccola "ciambella"
            color="Canale",
            color_discrete_map=colori
        )

        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="%{label}<br>%{value:,} bottiglie<br>%{percent}",
            pull=[0.02] * len(df)
        )

        return fig

    # Grafico: confronto vs mercato

    @app.callback(
        Output("grafico-confronto-mercato", "figure"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def confronto_mercato(_):
        # Dati cantina
        session = SessionLocal()
        query = text("""
            SELECT strftime('%Y', data) AS anno, SUM(quantità_venduta) AS bottiglie
            FROM vendite
            GROUP BY anno
        """)
        result = session.execute(query).fetchall()
        session.close()

        df_cantina = pd.DataFrame(result, columns=["anno", "vendite_cantina"])
        df_cantina["anno"] = df_cantina["anno"].astype(int)

        # CSV nazionale (assunto già importato come df_mercato globale)
        df_merge = pd.merge(df_mercato, df_cantina, on="anno", how="left")

        fig = px.line()
        fig.add_scatter(
            x=df_merge["anno"],
            y=df_merge["consumo_bottiglie"] / 1_000_000,  # milioni
            name="Consumo nazionale (milioni)",
            mode="lines+markers",
            line=dict(color="gray")
        )
        fig.add_scatter(
            x=df_merge["anno"],
            y=df_merge["vendite_cantina"],
            name="Vendite cantina",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#5e2b97")
        )

        fig.update_layout(
            title="VENDITE VS MERCATO",
            xaxis=dict(
                title="Anno",
                tickmode="linear",
                dtick=1
            ),
            yaxis=dict(
                title="Consumo nazionale (milioni di bottiglie)",
                showgrid=False
            ),
            yaxis2=dict(
                title="Vendite cantina (bottiglie)",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(x=0.01, y=0.99)
        )

        return fig

    # Grafico: Marketing vs vendite
    @app.callback(
        Output("grafico-marketing-vendite", "figure"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_marketing_vs_vendite(_):
        session = SessionLocal()

        # Query vendite
        query_vendite = text("""
            SELECT strftime('%Y', data) AS anno, SUM(quantità_venduta) AS bottiglie
            FROM vendite
            GROUP BY anno
            ORDER BY anno
        """)
        vendite_result = session.execute(query_vendite).fetchall()

        # Query marketing
        query_marketing = text("""
            SELECT anno, investimento_marketing
            FROM costi_annui
            ORDER BY anno
        """)
        marketing_result = session.execute(query_marketing).fetchall()
        session.close()

        # Costruzione DataFrame
        df_vendite = pd.DataFrame(vendite_result, columns=["anno", "bottiglie"])
        df_marketing = pd.DataFrame(marketing_result, columns=["anno", "marketing"])
        # Conversione anno in intero in entrambi i DF
        df_vendite["anno"] = df_vendite["anno"].astype(int)
        df_marketing["anno"] = df_marketing["anno"].astype(int)

        df = pd.merge(df_vendite, df_marketing, on="anno")

        df["anno"] = df["anno"].astype(int)
        df["bottiglie"] = df["bottiglie"].astype(int)
        df["marketing"] = df["marketing"].astype(float)

        # Creazione grafico
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["anno"],
            y=df["bottiglie"],
            name="Vendite (bottiglie)",
            mode="lines+markers",
            line=dict(color="#5e2b97")
        ))

        fig.add_trace(go.Scatter(
            x=df["anno"],
            y=df["marketing"],
            name="Marketing (€)",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#e67e22", dash="dash")
        ))

        fig.update_layout(
            title="MARKETING E VENDITE",
            xaxis=dict(
                title="Anno",
                tickmode="linear",
                dtick=1
            ),
            yaxis=dict(
                title="Vendite (bottiglie)",
                showgrid=False
            ),
            yaxis2=dict(
                title="Marketing (€)",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(x=0.01, y=0.99)
        )

        return fig

    # Grafico: produzione uva per anno
    @app.callback(
        Output("grafico-uva-annuale", "figure"),
        Input("dropdown-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_grafico_uva_per_anno(anno, _):
        session = SessionLocal()

        if anno == "all":
            query = text("""
                SELECT anno, u.nome AS tipo_uva, SUM(quantità_prodotta) AS totale
                FROM produzione p
                JOIN uva u ON p.id_uva = u.id
                GROUP BY anno, tipo_uva
                ORDER BY anno, tipo_uva
            """)
            params = {}
            titolo = "PRODUZIONE UVA VENDEMMIA"
        else:
            query = text("""
                SELECT anno, u.nome AS tipo_uva, SUM(quantità_prodotta) AS totale
                FROM produzione p
                JOIN uva u ON p.id_uva = u.id
                WHERE anno = :anno
                GROUP BY anno, tipo_uva
                ORDER BY tipo_uva
            """)
            params = {"anno": int(anno)}
            titolo = f"PRODUZIONE UVA VENDEMMIA - {anno}"

        result = session.execute(query, params).fetchall()
        session.close()

        df = pd.DataFrame(result, columns=["Anno", "Uva", "Kg"])

        fig = px.bar(
            df,
            x="Uva" if anno != "all" else "Anno",
            y="Kg",
            color="Uva",
            barmode="group",
            text="Kg",
            title=titolo
        )

        fig.update_traces(
            texttemplate="%{text:,} kg",
            textposition="inside"
        )

        fig.update_layout(
            yaxis_title="Quantità prodotta (kg)",
            xaxis_title="Anno" if anno == "all" else "Tipo uva",
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            legend_title="Tipo uva"
        )

        return fig

    # Dropdown anni per tabella magazzino
    @app.callback(
        Output("filtro-magazzino-anno", "options"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def popola_dropdown_magazzino(_):
        session = SessionLocal()
        query = text("SELECT DISTINCT anno FROM magazzino ORDER BY anno")
        result = session.execute(query).fetchall()
        session.close()
        return [{"label": "Tutte le annate", "value": "all"}] + [{"label": str(r[0]), "value": str(r[0])} for r in result]

    # Tabella dipendenti
    @app.callback(
        Output("tabella-dipendenti", "children"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_tabella_dipendenti(_):
        df = get_dipendenti()
        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#5e2b97', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )

    # Tabella ultime vendite
    @app.callback(
        Output("tabella-ultime-vendite", "children"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_tabella_vendite(_):
        df = get_ultime_vendite()
        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#5e2b97', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )

    # Tabella magazzino (modificabile)
    @app.callback(
        Output("tabella-magazzino", "children"),
        Input("filtro-magazzino-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def mostra_magazzino(anno, _):
        df = get_magazzino() if anno == "all" or anno is None else get_magazzino(anno)

        if df.empty:
            return html.Div("⚠️ Nessun dato disponibile")

        return dash_table.DataTable(
            columns=[{"name": col, "id": col, "editable": (col == "Prezzo")} for col in df.columns],
            data=df.to_dict("records"),
            id="magazzino-table-editable",
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#5e2b97', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
    
    @app.callback(
        Output("debug-check", "children"),  # serve solo a mostrare un messaggio
        Input("btn-aggiorna-prezzi", "n_clicks"),
        State("magazzino-table-editable", "data"),
        prevent_initial_call=True
    )
    def aggiorna_prezzi(n_clicks, righe_modificate):
        print(">>> Bottone cliccato. n_clicks =", n_clicks)
        if righe_modificate:
            session = SessionLocal()
            try:
                for riga in righe_modificate:
                    query = text("""
                        UPDATE magazzino
                        SET prezzo = :prezzo
                        WHERE anno = :anno AND tipo_vino = :tipo
                    """)
                    session.execute(query, {
                        "prezzo": riga["Prezzo"],
                        "anno": riga["Anno"],
                        "tipo": riga["Tipo Vino"]
                    })
                session.commit()
            finally:
                session.close()
        return "✅ Prezzi aggiornati!"
    
    #Indicatori valori ambientali
    @app.callback(
        Output("indicatori-terreno", "children"),
        Input("dropdown-anno", "value"),
        Input("aggiornamento-periodico", "n_intervals")
    )
    def aggiorna_indicatori_ambientali(anno, _):
        session = SessionLocal()

        if anno == "all":
            # Media delle somme annuali
            query = text("""
                WITH annuali AS (
                    SELECT
                        strftime('%Y', data) AS anno,
                        SUM(pioggia) AS pioggia_totale
                    FROM ambiente
                    GROUP BY anno
                )
                SELECT
                    (SELECT AVG(CASE 
                        WHEN strftime('%m', data) IN ('12','01','02') THEN temperatura END) FROM ambiente) AS inverno,
                    (SELECT AVG(CASE 
                        WHEN strftime('%m', data) IN ('03','04','05') THEN temperatura END) FROM ambiente) AS primavera,
                    (SELECT AVG(CASE 
                        WHEN strftime('%m', data) IN ('06','07','08') THEN temperatura END) FROM ambiente) AS estate,
                    (SELECT AVG(CASE 
                        WHEN strftime('%m', data) IN ('09','10','11') THEN temperatura END) FROM ambiente) AS autunno,
                    (SELECT AVG(umidita) FROM ambiente),
                    (SELECT AVG(vento) FROM ambiente),
                    (SELECT AVG(ore_di_sole) FROM ambiente),
                    (SELECT AVG(qualità_terreno) FROM ambiente),
                    (SELECT AVG(pioggia_totale) FROM annuali)
            """)
            result = session.execute(query).fetchone()
            session.close()

        else:
            query = text("""
                WITH filtrati AS (
                    SELECT * FROM ambiente
                    WHERE strftime('%Y', data) = :anno
                )
                SELECT
                    (SELECT AVG(temperatura) FROM filtrati WHERE strftime('%m', data) IN ('12','01','02')) AS inverno,
                    (SELECT AVG(temperatura) FROM filtrati WHERE strftime('%m', data) IN ('03','04','05')) AS primavera,
                    (SELECT AVG(temperatura) FROM filtrati WHERE strftime('%m', data) IN ('06','07','08')) AS estate,
                    (SELECT AVG(temperatura) FROM filtrati WHERE strftime('%m', data) IN ('09','10','11')) AS autunno,
                    (SELECT AVG(umidita) FROM filtrati),
                    (SELECT AVG(vento) FROM filtrati),
                    (SELECT AVG(ore_di_sole) FROM filtrati),
                    (SELECT AVG(qualità_terreno) FROM filtrati),
                    (SELECT SUM(pioggia) FROM filtrati)
            """)
            result = session.execute(query, {"anno": anno}).fetchone()
            session.close()

        # Scompone risultato
        stagioni = ["Inverno", "Primavera", "Estate", "Autunno"]
        inverno, primavera, estate, autunno, umidita, vento, sole, terreno, pioggia = result

        # Sostituisce None con 0
        valori = [inverno, primavera, estate, autunno, umidita, vento, sole, terreno, pioggia]
        valori = [round(v, 1) if v is not None else 0 for v in valori]
        inverno, primavera, estate, autunno, umidita, vento, sole, terreno, pioggia = valori

        def box(label, value, unit, emoji):
            return html.Div([
                html.H5(f"{emoji} {label}"),
                html.Div(f"{value} {unit}", style={"fontSize": "1.4rem", "fontWeight": "bold"})
            ], style={"flex": "1"})

        return html.Div([
            box("🌡️ Inverno", inverno, "°C", ""),
            box("🌡️ Primavera", primavera, "°C", ""),
            box("🌡️ Estate", estate, "°C", ""),
            box("🌡️ Autunno", autunno, "°C", ""),
            box("💧 Umidità", umidita, "%", ""),
            box("🌬️ Vento", vento, "km/h", ""),
            box("☀️ Ore di Sole", sole, "ore", ""),
            box("🌧️ Pioggia", pioggia, "mm", ""),
            box("🌱 Qualità Terreno", terreno, "", "")
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(9, 1fr)",  
            "gap": "1rem",
            "marginBottom": "2rem",
            "width": "100%"
        })
    
    #kill switch
    @app.callback(
        Output("btn-kill", "children"),
        Input("btn-kill", "n_clicks"),
        prevent_initial_call=True
    )
    def kill_switch(n_clicks):
        import os
        import threading

        def chiudi_dopo_1s():
            import time
            time.sleep(1)
            os._exit(0)

        threading.Thread(target=chiudi_dopo_1s).start()

        return "Dashboard chiusa. Ora puoi chiudere il browser."
        