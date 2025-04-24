from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Uva(Base):
    __tablename__ = 'uva'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    resa_attesa_ettaro = Column(Float, nullable=False)
    ettari = Column(Integer, nullable=False, default=3)
    resa_attesa = Column(Float, nullable=False) 


    produzioni = relationship("Produzione", back_populates="uva")

    def __init__(self, nome, resa_attesa_ettaro, ettari):
        self.nome = nome
        self.resa_attesa_ettaro = resa_attesa_ettaro
        self.ettari = ettari
        self.resa_attesa = self.resa_attesa_ettaro * self.ettari  # Calcoliamo la resa attesa

class Ambiente(Base):
    __tablename__ = 'ambiente'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    temperatura = Column(Float, nullable=False)
    umidita = Column(Float, nullable=False)
    qualità_terreno = Column(Float, nullable=False)
    pioggia = Column(Float, nullable=False)
    vento = Column(Float, nullable=False)
    ore_di_sole = Column(Float, nullable=False)

class Produzione(Base):
    __tablename__ = 'produzione'
    id = Column(Integer, primary_key=True)
    anno = Column(Integer, nullable=False)
    id_uva = Column(Integer, ForeignKey('uva.id'), nullable=False)
    quantità_prodotta = Column(Integer, nullable=False)
    qualità_annata = Column(Integer, nullable=False)  # da 1 a 10
    tipo_vino = Column(String)  # Nuovo campo per tipo di vino (Rosso, Bianco)
    # Collegamento con la tabella CostiAnnui per l'anno
    anno_costi = Column(Integer, ForeignKey('costi_annui.anno'))

    uva = relationship("Uva", back_populates="produzioni")
    costi = relationship("CostiAnnui", back_populates="produzioni")

class Magazzino(Base):
    __tablename__ = 'magazzino'
    id = Column(Integer, primary_key=True)
    anno = Column(Integer, nullable=False)  # anno della vendemmia
    tipo_vino = Column(String, ForeignKey('produzione.tipo_vino'))  # collegato al tipo_vino di Produzione
    bottiglie_tot = Column(Integer, nullable=False, default=0)
    bottiglie_disp = Column(Integer, nullable=False, default=0)
    prezzo = Column(Float, nullable=False, default=0.0)

    produzione = relationship("Produzione", backref="magazzino", primaryjoin="Magazzino.tipo_vino==Produzione.tipo_vino", viewonly=True)

class Vendite(Base):
    __tablename__ = 'vendite'
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    canale_vendita = Column(String)
    id_magazzino = Column(Integer, ForeignKey('magazzino.id'))  # Collegamento al lotto
    magazzino = relationship("Magazzino")
    tipo_vino = Column(String)
    quantità_venduta = Column(Integer)
    prezzo_unitario = Column(Float)
    incasso = Column(Float)

class CostiAnnui(Base):
    __tablename__ = 'costi_annui'

    anno = Column(Integer, primary_key=True)
    costo_materiali_per_bottiglia = Column(Float, nullable=False)
    ammortamento = Column(Integer, nullable=False)  # investimento inziale vigneti + macchinari / 25 anni
    investimento_marketing = Column(Integer, nullable=False)
    costo_personale = Column(Integer, nullable=False)
    inflazione_annua = Column(Float, nullable=False)

    produzioni = relationship("Produzione", back_populates="costi")

class Dipendente(Base):
    __tablename__ = "dipendenti"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    ruolo = Column(String, nullable=False)  # Es. 'Viticoltura', 'Produzione', 'Vendite', 'Amministrazione'
    stipendio_annuo = Column(Float, nullable=False)
    anno_assunzione = Column(Integer, nullable=False)
    attivo = Column(Boolean, default=True)
    
print ("tutto ok")