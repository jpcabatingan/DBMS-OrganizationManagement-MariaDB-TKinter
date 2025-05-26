import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'group4', 
    'password': 'group4', 
    'database': 'welove127' 
}

try:
    cnx = mysql.connector.connect(**DB_CONFIG)
    print("Successfully connected to the database!")

    
    cursor = cnx.cursor()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Access denied. Check your user name or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: Database does not exist. Please create it or check the name.")
    else:
        print(f"An unexpected error occurred: {err}")
finally:
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
        print("Database connection closed.")