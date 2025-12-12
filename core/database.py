import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "come_fit.db")
os.makedirs(os.path.join(PROJECT_ROOT, "database"), exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    menus = relationship("MenuGenerated", back_populates="user")
class MenuGenerated(Base):
    __tablename__ = "menus_generated"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    menu_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="menus")
def init_database():
    Base.metadata.create_all(engine)


