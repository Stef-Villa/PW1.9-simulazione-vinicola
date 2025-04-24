from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func
from app_generazione.models import Base, CostiAnnui, Uva, Ambiente, Produzione, Vendite, Magazzino, Dipendente 
from datetime import datetime, timedelta
import random
import calendar
import joblib
import pandas as pd
import numpy as np
from app_generazione.utils.conf import inflazione_storica


# calcolo inflazione annuale
def get_inflazione(anno, inflazione_storica):
    if 2019 <= anno <= 2024:
        return inflazione_storica[anno]
    else:
        # Calcola la media dell'inflazione reale passata
        media = sum(inflazione_storica.values()) / len(inflazione_storica)
        # Applica un margine di casualità: +/- 0.005 (0.5%)
        variazione = random.uniform(-0.005, 0.005)
        return round(media + variazione, 4)

# F GENERA DATI TABELLA UVA
def genera_dati_vigneti(session):
    varietà_uva = [
        {"nome": "Pinot Nero", "resa_attesa_ettaro": 5000, "ettari": 3},  # Resa per ettaro (5000 kg per ettaro per Pinot Nero)
        {"nome": "Berbera", "resa_attesa_ettaro": 9000, "ettari": 3}     # Resa per ettaro (8000 kg per ettaro per Moscato Bianco)
    ]

    for uva in varietà_uva:
        nuova_uva = Uva(
            nome=uva["nome"], 
            resa_attesa_ettaro=uva["resa_attesa_ettaro"], 
            ettari=uva["ettari"]
         )
        # Aggiungiamo il nuovo record al database
        session.add(nuova_uva)

    session.commit()
    print("DATI VIGNETI INSERITI CON SUCCESSO")

# F GENERA DATI AMBIENTALI
def genera_dati_ambientali(session):
    # Dati medi mensili zona 
    temperatura_mensile = {1: 3 , 2: 5 , 3: 9 , 4: 13 , 5: 17 , 6: 21 , 7: 24 , 8: 24 , 9: 20 , 10: 14 , 11: 8 , 12: 4}
    pioggia_mensile = {1: 28.8 , 2: 34.9 , 3: 45.4 , 4: 73.8 , 5: 82.1 , 6: 59.1 , 7: 40.0 , 8: 50.8 , 9: 66.5 , 10: 81.2 , 11: 75.4 , 12: 39.2}
    giorni_pioggia_mensile = {1: 3.5 , 2: 3.5 , 3: 5.4 , 4: 8.4 , 5: 9.5 , 6: 8.1 , 7: 6.3 , 8: 6.8 , 9: 6.7 , 10: 7.4 , 11: 6.3 , 12: 4.0}
    ore_sole_mensile = {1: 9.2, 2: 10.5, 3: 12.0 , 4: 13.6, 5: 14.9, 6: 15.6, 7: 15.2, 8: 14.0 , 9: 12.5 , 10: 10.9 , 11: 9.5, 12: 8.8}
    umidita_mensile = {1: 83 , 2: 80 , 3: 73 , 4: 76 , 5: 75 , 6: 74 , 7: 75, 8: 75 , 9: 76 , 10: 81 , 11: 84, 12: 84}
    vento_mensile = {1: 6.7 , 2: 7.7 , 3: 8.5 , 4: 8.5 , 5: 7.9 , 6: 7.2 , 7: 6.9 , 8: 6.6 , 9: 7.0 , 10: 6.9 , 11: 6.7 , 12: 6.4} 

    # Date dal 2019 a oggi
    start_date = datetime(2019, 1, 1)
    end_date = datetime.today()
    delta = timedelta(days=1)

    # Inizializzare la qualità del terreno con un valore casuale tra 0.85 e 1
    qualità_terreno = random.uniform(0.85, 1.0)  # Buon terreno iniziale
    
    # Iterazione per ogni giorno dal 2019 a oggi
    current_date = start_date
    mese_corrente = 1
    pioggia_totale_mese = 0
    while current_date <= end_date:
        mese = current_date.month
        temperatura_media = temperatura_mensile[mese]
        umidita_media = umidita_mensile[mese]
        pioggia_media = pioggia_mensile[mese]
        ore_sole_media = ore_sole_mensile[mese]
        vento_media = vento_mensile[mese]
        
        # Calcolare la temperatura giornaliera (distribuzione normale intorno alla media mensile)
        mu_temp = temperatura_media
        sigma_temp = 5  # Deviazione standard della temperatura
        temperatura = np.random.normal(mu_temp, sigma_temp)

        # Umidità giornaliera basata sulla media mensile con una deviazione standard
        umidita_giornaliera = random.gauss(umidita_media, 5)

        # numero di giorni piovosi nel mese con distribuzione normale
        giorni_pioggia = int(np.random.normal(giorni_pioggia_mensile[mese], 2))  # +/- 2 giorni di varianza
        giorni_pioggia = max(0, min(31, giorni_pioggia))  # Limite tra 0 e 31 giorni
        # Generazione giorni del mese in cui piove (in base al numero di giorni effettivi nel mese)
        giorni_del_mese = list(range(1, calendar.monthrange(current_date.year, current_date.month)[1] + 1))  # Giorni del mese
        giorni_piovosi = random.sample(giorni_del_mese, giorni_pioggia)  # Seleziona casualmente i giorni piovosi
        # Calcolo quantità totale di pioggia per il mese
        pioggia_totale = pioggia_media  # Pioggia totale del mese (mm)
        # Calcolp quantità di pioggia per ciascun giorno piovoso (distribuzione uniforme)
        se_pioggia_per_giorno = pioggia_totale / giorni_pioggia if giorni_pioggia > 0 else 0  # Media della pioggia giornaliera
        pioggia_per_giorno = np.random.uniform(se_pioggia_per_giorno * 0.9, se_pioggia_per_giorno * 1.1)  # Deviazione del 10% dalla media
        # Assegnazione pioggia ai giorni selezionati
        pioggia_giornaliera = 0
        if current_date.day in giorni_piovosi:
            # Imposta la pioggia giornaliera per i giorni piovosi
            pioggia_giornaliera = pioggia_per_giorno  # Intensità della pioggia (mm) per il giorno selezionato
        
        pioggia_totale_mese += pioggia_giornaliera # serivirà per ifnluenzare qualità terreno

        # Calcolo vento km/h e ore di sole (normali)
        vento = np.random.normal(vento_media, 1) 
        vento = max(0, min(vento, 20))

        ore_di_sole = np.random.normal(ore_sole_media, 1)

        # Correlazioni:
        if pioggia_giornaliera > se_pioggia_per_giorno:  # Se piove più del previsto, abbassa temperatura e umidità
            temperatura -= np.random.normal(2, 1)
            umidita_giornaliera += np.random.normal(3, 2)
        
        # Vento e ore di sole correlati
        if ore_di_sole >  ore_sole_media:  # Se ci sono più ore di sole, vento può aumentare
            vento += np.random.normal(2, 1)
        elif ore_di_sole <  ore_sole_media:  # Se ci sono meno ore di sole, vento può diminuire
            vento -= np.random.normal(2, 1)

        # Aggiustamento finale per le ore di sole se piove molto
        if pioggia_giornaliera > 40:  # Se piove molto (>40 mm), ridurre drasticamente le ore di sole
            ore_di_sole -= np.random.normal(3, 1)

        #arrotondamenti
        temperatura = round(temperatura, 1)
        umidita_giornaliera = round(umidita_giornaliera, 1)
        pioggia_giornaliera = round(pioggia_giornaliera, 1)
        vento = round(vento, 1)
        ore_di_sole = round(ore_di_sole, 1)

       # Coefficienti giornalieri
        coeff_temp = 0.004
        coeff_vento = 0.002
        coeff_sole = 0.002

        # Scostamenti normalizzati rispetto alla media mensile del giorno corrente
        delta_temp = (temperatura - temperatura_media) / temperatura_media
        delta_vento = (vento - vento_media) / vento_media
        delta_sole = (ore_di_sole - ore_sole_media) / ore_sole_media

        # Somma delle variazioni quotidiane
        delta_qualità_giornaliera = (
            coeff_temp * delta_temp +
            coeff_vento * delta_vento +
            coeff_sole * delta_sole
        )

        qualità_terreno += delta_qualità_giornaliera

        # Alla fine del mese: effetto mensile della pioggia
        if current_date.month != mese_corrente:
            delta_pioggia = (pioggia_totale_mese - pioggia_media) / pioggia_media
            coeff_pioggia = 0.01  # più alto, perché la pioggia è valutata una volta sola
            qualità_terreno += coeff_pioggia * delta_pioggia

            # Reset pioggia mensile
            pioggia_totale_mese = 0
            mese_corrente = current_date.month

        # qualità del terreno tra 0 e 1
        qualità_terreno = round(max(0, min(1, qualità_terreno)), 2)
            
        # Aggiunta dati al database
        ambiente = Ambiente(
            data=current_date, 
            temperatura=temperatura,
            umidita=umidita_giornaliera,
            qualità_terreno=qualità_terreno,
            pioggia=pioggia_giornaliera,
            vento=vento,
            ore_di_sole=ore_di_sole
        )
        session.add(ambiente)
        
        current_date += delta

    session.commit()
    print(f"Dati ambientali generati fino al {end_date}")

def genera_dati_produzione(session, rf_model):
    # Recupero i dati annuali dal database (tabella "ambiente")
    # Calcolo media annuale per temp_media, umidita_media, vento_kmh
    # e totale annuale per pioggia_mm

    query = session.query(
        func.extract('year', Ambiente.data).label('anno'),
        func.avg(Ambiente.temperatura).label('temp_media'),
        func.avg(Ambiente.umidita).label('umidita_media'),
        func.avg(Ambiente.vento).label('vento_kmh'),
        func.sum(Ambiente.pioggia).label('pioggia_mm'),
        func.avg(Ambiente.qualità_terreno).label('qualita_terreno_media')
    ).group_by(func.extract('year', Ambiente.data)).all()

    # Lista per contenere i dati da inserire nella tabella "Produzione"
    dati_produzione = []
    
    # Prende l'anno corrente
    anno_corrente = pd.to_datetime("today").year

     # Resa massima per vigneto
    resa_max_pinot_nero = 15000
    resa_max_barbera = 27000  
    
    
    for anno_dati in query:
        # Esclude l'anno corrente (2025 se non è ancora finito)
        anno = anno_dati.anno
        if anno == anno_corrente:
            print(f"Salto l'anno {anno} perché non è completo")
            continue
        
        # Estrazione dei valori annuali
        temp_media = anno_dati.temp_media
        umidita_media = anno_dati.umidita_media
        vento_kmh = anno_dati.vento_kmh
        pioggia_mm = anno_dati.pioggia_mm
        qualita_terreno_media = anno_dati.qualita_terreno_media
        
        # Creazione di un DataFrame per passare al modello
        df_ambientale = pd.DataFrame({
            'temp_media': [temp_media],
            'umidita_media': [umidita_media],
            'pioggia_mm': [pioggia_mm],
            'vento_kmh': [vento_kmh]
        })
        
        # Previsione della produzione per ettaro per l'anno corrente
        produzione_per_ettaro = rf_model.predict(df_ambientale)[0]  # Prendi il primo risultato

        # Aggiunge quantità prodotta nella variabile di produzione
        # 3 ettari di vigneto
        quantità_prodotta_q = produzione_per_ettaro * 3
        quantità_prodotta_kg = round(quantità_prodotta_q * 100)

         # Indice di casualità per differenziare la produzione
        casualita = random.uniform(0.90, 1.10)  # Indice di casualità tra -10% e +10%
        
        # coefficienti per avere proporzionalità tra le due produzioni
        coef_pinot = 0.3571  # Coefficiente per Pinot Nero (5000/14000)
        coef_barbera = 0.6429    # Coefficiente per Barbera (9000/14000)

        produzione_pinot_nero = min(round(2 * quantità_prodotta_kg * coef_pinot * casualita), resa_max_pinot_nero)  # Limita alla resa massima per ettaro
        produzione_barbera = min(round(2 * quantità_prodotta_kg * coef_barbera * casualita), resa_max_barbera)  # Limita alla resa massima per ettaro

        qualita_annata = round(qualita_terreno_media * 10, 2)

        # Crea due righe per ogni anno: una per Barbera e una per Pinot Nero
        # Uva Pinot Nero
        
        dati_produzione.append({
            'anno': anno,
            'id_uva': 1,  
            'quantità_prodotta': produzione_pinot_nero, 
            'tipo_vino': 'Pinot Nero',
            'anno_costi': anno,
            'qualità_annata': qualita_annata
        })

        # Uva Barbera 
        
        dati_produzione.append({
            'anno': anno,
            'id_uva': 2,  
            'quantità_prodotta': produzione_barbera, 
            'tipo_vino': 'Barbera DOP',
            'anno_costi': anno,
            'qualità_annata': qualita_annata
        })


    # Aggiunta dati produzione al database
    session.bulk_insert_mappings(Produzione, dati_produzione)
    session.commit()

    print("Dati di produzione generati con successo!")

def popola_dipendenti(session):
    lista_dipendenti = [
        # Viticoltura
        {"nome": "Luca", "ruolo": "Viticoltura", "stipendio_annuo": 21000, "anno_assunzione": 2019},
        {"nome": "Marco", "ruolo": "Viticoltura", "stipendio_annuo": 21000, "anno_assunzione": 2019},
        {"nome": "Giulia", "ruolo": "Viticoltura", "stipendio_annuo": 21000, "anno_assunzione": 2019},
        {"nome": "Sara", "ruolo": "Viticoltura", "stipendio_annuo": 21000, "anno_assunzione": 2019},

        # Produzione
        {"nome": "Alessio", "ruolo": "Produzione", "stipendio_annuo": 21000, "anno_assunzione": 2019},
        {"nome": "Valentina", "ruolo": "Produzione", "stipendio_annuo": 21000, "anno_assunzione": 2019},

        # Vendite
        {"nome": "Francesca", "ruolo": "Vendite", "stipendio_annuo": 23000, "anno_assunzione": 2019}
    ]

    for d in lista_dipendenti:
        nuovo_dip = Dipendente (
            nome=d["nome"],
            ruolo=d["ruolo"],
            stipendio_annuo=d["stipendio_annuo"],
            anno_assunzione=d["anno_assunzione"],
            attivo=True
        )
        session.add(nuovo_dip)

    session.commit()
    print("Dipendenti inseriti con successo.")

def genera_dati_costi_annui(session):

    def calcola_costo_materiali(anno, costo_base=2.00):
        inflazione_tot = 1.0
        for a in range(2019, anno + 1):
            inflazione_annuale = inflazione_storica.get(a, 0.02)  # fallback 2%
            inflazione_tot *= (1 + inflazione_annuale)
        return round(costo_base * inflazione_tot, 2)
    
    anni = range(2019, 2026)
    investimento_iniziale = 2_500_000
    anni_ammortamento = 25
    ammortamento_annuo = investimento_iniziale / anni_ammortamento
   
    for anno in anni:
        inflazione = get_inflazione(anno, inflazione_storica)

        # Calcolo costo materiali per l’anno, considerando inflazione
        costo_materiali = calcola_costo_materiali(anno)

        # Calcolo costo personale
        dipendenti_attivi = session.query(Dipendente).filter(
            Dipendente.anno_assunzione <= anno,
            Dipendente.attivo == True
        ).all()
        costo_personale = sum(d.stipendio_annuo for d in dipendenti_attivi)

        # Imposta solo il marketing iniziale.
        # Gli anni successivi verranno aggiornati dopo aver generato le vendite.
        if anno == 2019:
            investimento_marketing = 20000
        else:
            investimento_marketing = 0

        costi = CostiAnnui(
            anno=anno,
            costo_materiali_per_bottiglia=costo_materiali,
            ammortamento=ammortamento_annuo,
            investimento_marketing=investimento_marketing,
            costo_personale=costo_personale,
            inflazione_annua=inflazione
        )
        session.add(costi)

    session.commit()
    print("Costi annui generati con successo.")

def calcola_prezzo(session, anno, qualità_annata, tipo_vino):
  
    anno_costi = 2019 if anno in [2016, 2017, 2018] else anno
    costi = session.query(CostiAnnui).filter(CostiAnnui.anno == anno_costi).first()
    if not costi:
        print(f"Costi mancanti per l'anno {anno}.")
        return 0.0


    anno_costi = 2019 if anno in [2016, 2017, 2018] else anno
    produzioni = session.query(Produzione).filter(Produzione.anno == anno_costi).all()
    if not produzioni:
        print(f"Nessuna produzione registrata per l'anno {anno}")
        return 0.0

    # Bottiglie prodotte per ogni vino
    bottiglie_per_vino = {}
    totale_bottiglie = 0

    for p in produzioni:
        bottiglie = int(p.quantità_prodotta * 0.7 / 0.75)
        bottiglie_per_vino[p.tipo_vino] = bottiglie
        totale_bottiglie += bottiglie

    if tipo_vino not in bottiglie_per_vino or bottiglie_per_vino[tipo_vino] == 0:
        print(f"Nessuna produzione di {tipo_vino} per l'anno {anno}")
        return 0.0

    quota = bottiglie_per_vino[tipo_vino] / totale_bottiglie

    # Costi proporzionati
    costo_totale_vino = (
        costi.costo_materiali_per_bottiglia * bottiglie_per_vino[tipo_vino] +
        costi.ammortamento * quota +
        costi.investimento_marketing * quota +
        costi.costo_personale * quota
    )

    costo_unitario = costo_totale_vino / bottiglie_per_vino[tipo_vino]
    base = round(costo_unitario * 1.5, 2)

    # Influenza della qualità
    if qualità_annata >= 9:
        prezzo = base * 1.2
    elif qualità_annata >= 7:
        prezzo = base
    elif qualità_annata >= 5:
        prezzo = base * 0.9
    else:
        prezzo = base * 0.75

    # Arrotondamento a intero o .5
    return round(prezzo * 2) / 2


def genera_dati_magazzino(session):
    anno_attuale = datetime.now().year

    # Giacenza simulata per anni 2016–2018
    def calcola_media_produzione():
        media = {}
        tipi_vino = ["Pinot Nero", "Barbera DOP"]
        for tipo in tipi_vino:
            records = session.query(Produzione).filter(
                Produzione.anno >= 2019,
                Produzione.anno <= 2023,
                Produzione.tipo_vino == tipo
            ).all()
            if records:
                media[tipo] = sum(p.quantità_prodotta for p in records) / len(records)
            else:
                media[tipo] = 2000
        return media

    media_produzione = calcola_media_produzione()
    annate_giacenza = [2016, 2017, 2018]
    tipi_vino = ["Pinot Nero", "Barbera DOP"]

    for anno in annate_giacenza:
        for tipo in tipi_vino:
            base = media_produzione[tipo]
            casualità = random.uniform(0.9, 1.1)
            quantità_kg = int(base * casualità)

            if anno == 2016:
                quantità_kg = int(quantità_kg * 0.25)

            bottiglie = int(quantità_kg * 0.7 / 0.75)
            qualità = round(random.uniform(7.0, 9.5), 2)
            prezzo = calcola_prezzo(session, anno, qualità, tipo)

            magazzino = Magazzino(
                anno=anno,
                tipo_vino=tipo,
                bottiglie_tot=bottiglie,
                bottiglie_disp=bottiglie,
                prezzo=prezzo
            )
            session.add(magazzino)

    # Produzione vera fino a anno_attuale
    produzioni = session.query(Produzione)\
        .filter(Produzione.anno <= anno_attuale - 2)\
        .all()

    for produzione in produzioni:
        anno_vendemmia = produzione.anno
        if anno_vendemmia < 2019:
            continue  # Già gestita sopra

        bottiglie = int(produzione.quantità_prodotta * 0.7 / 0.75)
        qualità = produzione.qualità_annata
        tipo_vino = produzione.tipo_vino
        prezzo = calcola_prezzo(session, anno_vendemmia, qualità, tipo_vino)

        magazzino = Magazzino(
            anno=anno_vendemmia,
            tipo_vino=tipo_vino,
            bottiglie_tot=bottiglie,
            bottiglie_disp=bottiglie,
            prezzo=prezzo
        )
        session.add(magazzino)

    session.commit()
    print("Magazzino generato con prezzi calcolati da costi annui e qualità.")

def festivita_italiane(anno):
        from dateutil.easter import easter
        return set([
            datetime(anno, 1, 1).date(),   # Capodanno
            datetime(anno, 1, 6).date(),   # Epifania
            datetime(anno, 12, 25).date(), # Natale
            datetime(anno, 12, 26).date(), # Santo Stefano
            easter(anno),  # Pasqua
            easter(anno) + timedelta(days=1),  # Pasquetta
            datetime(anno, 8, 15).date()   # Ferragosto  
        ])

def genera_vendite_storiche(session):
    oggi = datetime.now().date()
    anno_corrente = oggi.year
    anno_inizio = 2019
    anni = list(range(anno_inizio, anno_corrente + 1))

    for anno in anni:
        produzione_disponibile = session.query(func.sum(Magazzino.bottiglie_disp)).filter(
            Magazzino.anno <= anno - 2,
            Magazzino.bottiglie_disp > 0
        ).scalar() or 0

        inflazione = session.query(CostiAnnui.inflazione_annua).filter(CostiAnnui.anno == anno).scalar() or 0.02

        base = 0.85
        penalty = max(0.85, 1 - inflazione * 2)
        casuale = random.uniform(0.9, 1.1)
        stima_vendite_annuali = int(produzione_disponibile * base * penalty * casuale)

        if anno == anno_corrente:
            giorni_totali = (datetime(anno, 12, 31) - datetime(anno, 1, 1)).days + 1
            giorni_passati = (oggi - datetime(anno, 1, 1).date()).days + 1
            fattore_parziale = giorni_passati / giorni_totali
            stima_vendite_annuali = int(stima_vendite_annuali * fattore_parziale)

        vendite_effettive_anno = 0

        quote = np.random.dirichlet([3, 2, 2, 2])
        percentuali_canale = dict(zip(["cantina", "online", "ristoranti", "export"], quote))

        inizio = datetime(anno, 1, 1).date()
        fine = oggi if anno == anno_corrente else datetime(anno, 12, 31).date()
        calendario = pd.date_range(start=inizio, end=fine)

        festivita = festivita_italiane(anno)

        for canale, quota in percentuali_canale.items():
            da_vendere = int(stima_vendite_annuali * quota)

            giorni_attivi = [d for d in calendario
                             if d.weekday() in CANALI[canale]['attivo_giorni']
                             and (canale == 'online' or d not in festivita)]

            if not giorni_attivi:
                continue

            pesi = []
            for giorno in giorni_attivi:
                peso = 1.0
                if giorno.month in STAGIONALITA:
                    peso *= STAGIONALITA[giorno.month]
                if canale == "cantina" and giorno.weekday() >= 5:
                    peso *= 1.2
                pesi.append(peso)

            pesi = np.array(pesi)
            pesi /= pesi.sum()
            distribuzione = np.random.multinomial(da_vendere, pesi)

            for giorno, num_bottiglie in zip(giorni_attivi, distribuzione):
                while num_bottiglie > 0 and vendite_effettive_anno < stima_vendite_annuali:
                    max_ordine = min(num_bottiglie, CANALI[canale]['max_bottiglie'])
                    min_ordine = CANALI[canale]['min_bottiglie']
                    if num_bottiglie < min_ordine:
                        break

                    quantita = random.randint(min_ordine, max_ordine)
                    if vendite_effettive_anno + quantita > stima_vendite_annuali:
                        quantita = stima_vendite_annuali - vendite_effettive_anno

                    sconto = CANALI[canale].get("sconto", 0.0)
                    tipo_vino = random.choices(['Barbera DOP', 'Pinot Nero'], weights=[0.6, 0.4])[0]

                    lotti = session.query(Magazzino).filter(
                        Magazzino.tipo_vino == tipo_vino,
                        Magazzino.bottiglie_disp > 0,
                        Magazzino.anno <= anno - 2
                    ).order_by(Magazzino.anno.asc()).all()

                    for lotto in lotti:
                        if lotto.bottiglie_disp >= quantita:
                            lotto.bottiglie_disp -= quantita
                            session.add(Vendite(
                                data=giorno,
                                canale_vendita=canale,
                                id_magazzino=lotto.id,
                                tipo_vino=lotto.tipo_vino,
                                quantità_venduta=quantita,
                                prezzo_unitario=lotto.prezzo,
                                incasso=round(quantita * lotto.prezzo * (1 - sconto), 2)
                            ))
                            vendite_effettive_anno += quantita
                            break
                    num_bottiglie -= quantita

    session.commit()
    print("Vendite generate dal 2019 a oggi.")

def aggiorna_investimento_marketing (session):
    anni = session.query(CostiAnnui.anno).all()
    anni = [a[0] for a in anni if a[0] > 2019]  # Salta il primo anno

    for anno in anni:
        vendite_precedenti = session.query(Vendite).join(Magazzino).filter(
            Vendite.data >= datetime(anno - 1, 1, 1),
            Vendite.data <= datetime(anno - 1, 12, 31)
        ).all()

        totale = sum(v.incasso for v in vendite_precedenti)
        investimento = round(totale * 0.05, 2)  # 5%

        costi = session.query(CostiAnnui).filter(CostiAnnui.anno == anno).first()
        if costi:
            costi.investimento_marketing = round(investimento)
            # print(f"Aggiornato marketing {anno}: {investimento} €")

    session.commit()

    
CANALI = {
    "cantina": {
        "attivo_giorni": [2, 3, 4, 5, 6],  # mer -> dom
        "min_bottiglie": 1,
        "max_bottiglie": 6,
        "sconto": 0.0
    },
    "online": {
        "attivo_giorni": list(range(7)),  # tutti i giorni
        "min_bottiglie": 1,
        "max_bottiglie": 12,
        "sconto": 0.0
    },
    "ristoranti": {
        "attivo_giorni": list(range(7)),
        "min_bottiglie": 18,
        "max_bottiglie": 36,
        "sconto": 0.25
    },
    "export": {
        "attivo_giorni": list(range(7)),
        "min_bottiglie": 6,
        "max_bottiglie": 24,
        "sconto": 0.0
    }
}

STAGIONALITA = {
    3: 1.15,  # Marzo
    4: 1.15,  # Aprile
    8: 1.15,  # Agosto
    12: 1.25  # Dicembre
}


def genera_tutti_i_dati(session, rf_model):
    np.random.seed(7)

    # inseriamo i dati richiamando le funzioni
    genera_dati_vigneti(session)
    genera_dati_ambientali(session)
    genera_dati_produzione(session, rf_model)
    popola_dipendenti(session)
    genera_dati_costi_annui(session)
    genera_dati_magazzino(session)
    genera_vendite_storiche (session)
    aggiorna_investimento_marketing (session)

    session.close()

    print("Dati inseriti con successo.")
