from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    chips = Column(Float, default=0.0) # Üyenin çip parası
    # Üyenin botuyla olan ilişkisi
    bot = relationship("Bot", back_populates="owner", uselist=False)

class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bot_name = Column(String)
    mining_power = Column(Float, default=0.0) # Madencilik kapasitesi
    
    owner = relationship("User", back_populates="bot")

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String)
    prediction = Column(String) # Lotofoot kombinasyonu gibi
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
