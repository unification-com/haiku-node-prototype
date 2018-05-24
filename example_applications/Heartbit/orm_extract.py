from orm_main import Session, engine, Base
from orm_table_users import User
from orm_table_userdata import UserData
from pprint import pprint

session = Session()

#	Extract users. This is where query (filtering/joining) happens
#users = session.query(User).all()
#data = session.query(UserData).all()

joined = session.query(UserData) \
	.join(User) \
	.all()
	
# Show users (debug)
if False:
	print('\n### All users:')
	for user in users:
		print(user.FirstName, "has lastname", user.LastName, "with Email:",user.Email)
	print('')

# Show userdata (debug)
if False:
	print('\n### All data:')
	for datablock in data:
		print("DataID:", datablock.DataID, "Heartrate:", datablock.Heartrate, "Loc:", datablock.GeoLocation, "Time:", datablock.TimeStamp, "Pulse:", datablock.Pulse)
	print('')

# Show joined data
if True:
	for joinedbloc in joined:
		#pprint(vars(joinedbloc))
		print("DataID:", joinedbloc.DataID, "Heartrate:", joinedbloc.Heartrate, "Loc:", \
			joinedbloc.GeoLocation, "Time:", joinedbloc.TimeStamp, "Pulse:", joinedbloc.Pulse, \
			"UserID:", joinedbloc.UserID)
		# NOTE: This join did not include joined column object fields from the Users table. 
		# Maybe we need a different join call? Like, a full join? Or something?
	print('')
