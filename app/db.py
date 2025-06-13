from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base
# from app.models import processed_price_points, symbol_average

DATABASE_URL = "postgresql://nadkar:password@localhost:5432/market_data_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created.")
