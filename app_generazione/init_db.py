from app_generazione.models import Base

def crea_database(engine):
    Base.metadata.create_all(engine)
    print("Database creato.")