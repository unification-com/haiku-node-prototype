import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime

log = logging.getLogger(__name__)

Base = declarative_base()


class Request(Base):
    __tablename__ = 'request'

    id = Column(Integer, primary_key=True)
    consumer = Column(String)
    users = Column(String)
    schema_id = Column(Integer)
    columns = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
