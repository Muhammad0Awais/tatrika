from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import create_session

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    phone_number = Column(String)
    current_state = Column(String)
    default_state = Column(String, default="UndefinedKoala")
    last_sended_message_id = Column(Integer)


engine = create_engine("sqlite:///prodb.db")
Base.metadata.create_all(engine)
