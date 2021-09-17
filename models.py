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
    username = Column(String)
    phone_number = Column(String)
    current_state = Column(String)
    default_state = Column(String, default="UndefinedKoala")
    last_sended_message_id = Column(Integer)
    onboarding_page = Column(Integer, default=1)
    questions = relationship("Question", backref="customer")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    text = Column(String(121))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="unanswered")


engine = create_engine("sqlite:///prodb.db")
Base.metadata.create_all(engine)
