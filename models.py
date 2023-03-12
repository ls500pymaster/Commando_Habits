import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    difficulty = Column(Enum("low", "medium", "high"), default="low")
    days = Column(Integer)
    user_id = Column(Integer, index=True)


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('habits.db')
        return conn
    except Error as e:
        print(e)

    return conn


SQLALCHEMY_DATABASE_URL = "sqlite:///./habits.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
