from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String)
    username = Column(String)
    role = Column(String)
    rating = Column(Float, default=0.0)
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    status = Column(String, default='active')
    user_id = Column(Integer, ForeignKey('users.telegram_id'))
    user = relationship("User", back_populates="orders")
    created_at = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = "sqlite:///data/database.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)