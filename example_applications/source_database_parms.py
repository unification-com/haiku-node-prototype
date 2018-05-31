heartbit_data_source_parms = {
    'odbc':'mysql+mysqldb',
    'database':'Heartbit',
    'host':'localhost',
    'user':'Heartbit',
    'pass':'Heartbit',
    'userTable':'Users',
    'dataTable':'UserData',
    'userIdentifier':'ID',
    'dataUserIdentifier':'UserID',
    'dataColumnsToInclude':['Heartrate','GeoLocation','TimeStamp','Pulse']
}

blobdata_data_source_parms = {
    'odbc':'mysql+mysqldb',
    'database':'Datablobs',
    'host':'localhost',
    'user':'Datablobs',
    'pass':'Datablobs',
    'userTable':'BlobCreator',
    'dataTable':'BlobData',
    'userIdentifier':'CreatorID',
    'dataUserIdentifier':'CreatorID',
    'dataColumnsToInclude':['DataBlob','BlobSize']
}

file_data_source_parms = {
    'odbc':'mysql+mysqldb',
    'database':'Heartbit',
    'host':'localhost',
    'user':'Heartbit',
    'pass':'Heartbit',
    'userTable':'',
    'dataTable':'',
    'userIdentifier':'',
    'dataUserIdentifier':'',
    'dataColumnsToInclude':[]
}