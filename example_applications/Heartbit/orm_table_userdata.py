from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from orm_main import Base

class UserData(Base):
	__tablename__ = 'UserData'

	DataID = Column(Integer, primary_key=True)
	Heartrate = Column(Integer)
	GeoLocation = Column(Integer)
	TimeStamp = Column(DateTime)
	Pulse = Column(Integer)
	
	UserID = Column(Integer, ForeignKey('Users.ID'))