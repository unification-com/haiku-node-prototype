from transform_data import fetch_user_data
from source_database_parms import *

if __name__ == '__main__':
    res = fetch_user_data(heartbit_data_source_parms)
    print(res)