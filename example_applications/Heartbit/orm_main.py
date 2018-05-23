from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime

connString = 'mysql+mysqldb://Heartbit:Heartbit@localhost/Heartbit'

engine = create_engine(connString)
Session = sessionmaker(bind=engine)
Base = declarative_base()