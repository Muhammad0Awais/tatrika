from collections import UserList
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import create_session, relation, relationship
import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    phone_number = Column(String(50))
    current_state = Column(String(50))
    default_state = Column(String(50), default="UndefinedKoala")
    last_sended_message_id = Column(Integer)
    onboarding_page = Column(Integer, default=1)
    questions = relationship("Question", backref="customer")
    game_card = relationship("GameCard", backref="customer", uselist=False)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    text = Column(String(121))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="unanswered")


class GameCard(Base):
    __tablename__ = "game_card"
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    id = Column(Integer, primary_key=True)


class CardsGame(Base):
    __tablename__ = "cards_game"
    id = Column(Integer, primary_key=True, autoincrement=True)
    correct_answer = Column(String(121))
    answers = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="unanswered")


cnx = {
    "connector": "mysql+pymysql",
    "user": "a0560710",
    "password": "veipsaihfe",
    "host": "a0560710.xsph.ru",
    "database": "a0560710_prod_db",
}


engine = create_engine(
    "{connector}://{user}:{password}@{host}/{database}".format(**cnx)
)

Base.metadata.create_all(engine)
