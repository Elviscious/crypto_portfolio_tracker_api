from sqlalchemy import create_engine, Float, String, Integer, Column, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


DATABASE_URL = "postgresql+psycopg2://postgres:2345@localhost/crypto_tracker_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    coin_symbol = Column(String, index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)
    percent_change = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.now())


def create_tables():
    # Drop all tables first
    Base.metadata.drop_all(bind=engine)
    # Then create them with the new schema
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
