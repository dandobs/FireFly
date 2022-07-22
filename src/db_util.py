import mysql.connector
from mysql.connector import Error
import io


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name, user=user_name, passwd=user_password, database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def execute_query(connection, query, params=()):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


def read_query(connection, query, params=()):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


def getFlightNum(self):
    query = "SELECT max(flightNum) from image_records;"
    res = read_query(self.sqlConn, query)
    if res:
        return res[0][0]
    else:
        return 1