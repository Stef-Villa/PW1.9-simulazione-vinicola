from dash import html, dcc

layout = html.Div(
    className="page",
    children=[

        dcc.Interval(
            id="aggiornamento-periodico",
            interval=60 * 1000,
            n_intervals=0
        ),


        # Header con titolo centrato, dropdown a destra
        html.Div([
            html.Div([
                html.H1("La Mia Cantina", className="page-title")
            ], className="header-center"),

            html.Div([
                html.Label("Seleziona anno:", className="label"),
                dcc.Dropdown(
                    id="dropdown-anno",
                    options=[{"label": "Tutti gli anni", "value": "all"}],
                    value="all",
                    clearable=False,
                    className="dropdown"
                )
            ], className="header-anno")
        ], className="header"),

        # Indicatori ambientali
        html.Div([
            html.Div([
                html.H3("Indicatori ambientali", className="section-title"),
                html.A("Scarica CSV",
                    id="scarica-csv",
                    download="dati_ambiente.csv",
                    href="/scarica-csv",
                    target="_blank",
                    className="button"
                )
            ], className="card-header"),

            html.Div(id="indicatori-terreno", className="card indicatori")
        ], className="card mb-2"),

        # Prima riga grafici: vendite, incassi, margini
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-vendite-annuali", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-incassi-annuali", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-margini-annuali", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),
        ], className="row"),

        # Seconda riga: vendite per mese / tipo vino / canale
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-vendite-mensili", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-ripartizione-vini", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-canali", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),
        ], className="row"),

        # Terza riga: confronto + marketing + uva
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-confronto-mercato", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-marketing-vendite", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),

            html.Div([
                dcc.Graph(id="grafico-uva-annuale", style={"width": "100%", "height": "auto"})
            ], className="card grafico"),
        ], className="row"),

        # Quarta riga: magazzino, dipendenti, ultime vendite
        html.Div([
            html.Div([
                html.H3("Magazzino", className="section-title"),
                html.Label("Annata:", className="label"),
                dcc.Dropdown(id="filtro-magazzino-anno", clearable=False, value="all", className="dropdown"),
                
                html.Div(id="tabella-magazzino"),

                html.Div([
                    html.Div(id="debug-check", className="debug", style={"flex": "1"}),
                    html.Button("Aggiorna Prezzi", id="btn-aggiorna-prezzi", className="button", style={"alignSelf": "flex-end"})
                ], style={
                    "display": "flex",
                    "justifyContent": "flex-end",
                    "marginTop": "1rem"
                })

            ], className="card col-1-3"),

            html.Div([
                html.H3("Dipendenti", className="section-title"),
                html.Div(id="tabella-dipendenti")
            ], className="card col-1-3"),

            html.Div([
                html.H3("Ultime 10 vendite", className="section-title"),
                html.Div(id="tabella-ultime-vendite")
            ], className="card col-1-3"),
        ], className="row"),

        #kill switch
        html.Div([
            html.Button("Termina processo dashboard", id="btn-kill", className="button-kill")
        ], className="kill-container")
        
    ]
)