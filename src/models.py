from sqlalchemy import Column, Integer, String, Float

from database import Base


class CurrencyRates(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    symbol_from = Column(String, index=True)
    symbol_to = Column(String, index=True)
    rate = Column(Float(10, 2))
