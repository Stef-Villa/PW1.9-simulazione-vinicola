from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///data/cantina.db", future=True)
SessionLocal = sessionmaker(bind=engine)
