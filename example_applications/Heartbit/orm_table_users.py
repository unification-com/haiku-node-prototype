from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import relationship
from orm_main import Base

class User(Base):
	__tablename__ = 'Users'
	
	ID = Column(Integer, primary_key=True)
	LastName = Column(String, nullable=False)
	FirstName = Column(String, nullable=False)
	Email = Column(String, nullable=False)
	GenderCode = Column(Integer)
	
	data = relationship("UserData")