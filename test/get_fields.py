from sqlalchemy import create_engine

conn_string ='mysql+mysqlconnector://datablobs_user:password@db:3306/Datablobs'

engine = create_engine(conn_string)

query = 'SHOW FIELDS FROM BlobCreator'

print(query)

t = engine.execute(query)

result = [r[0] for r in t]
print(result)
