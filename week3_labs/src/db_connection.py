import mysql.connector

def connect_db():
    return mysql.connector.connect(host="localhost", user="root", password="djpim!", database="fletapp", connection_timeout=5)
