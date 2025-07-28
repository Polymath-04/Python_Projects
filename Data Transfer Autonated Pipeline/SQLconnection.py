from sqlalchemy import create_engine
import Variable_Config as v

def create_connection():
    # create a connection to the database
    try:
        connection_string = f'mssql+pyodbc://{v.DB_USER}:{v.DB_PASSWORD}@{v.DB_SERVER}/{v.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&MARS_Connection=Yes'
        engine = create_engine(connection_string)
        x=engine.connect()
        x.close()
        engine.dispose()
        return engine
    except Exception as e:
        raise Exception(f"Connection Failed: {e}")

test_connection=False
if test_connection:
    try:
        engine=create_connection()
        x=engine.connect()
        x.close()
        engine.dispose()
        print("Connection Created Successfully")
        print(engine)
    except Exception as e:
        raise Exception(f"Connection Failed: {e}")
        
