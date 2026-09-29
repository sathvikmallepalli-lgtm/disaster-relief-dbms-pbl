"""Small MySQL connection helpers shared by the prototype and web application."""

import os

import mysql.connector


def get_connection():
    options = {
        "user": os.environ.get("DB_USER", "relief_app"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "disaster_relief"),
        "autocommit": False,
    }
    if os.environ.get("DB_SOCKET"):
        options["unix_socket"] = os.environ["DB_SOCKET"]
    else:
        options["host"] = os.environ.get("DB_HOST", "127.0.0.1")
        options["port"] = int(os.environ.get("DB_PORT", "3306"))
    return mysql.connector.connect(**options)


def fetch_all(statement, parameters=()):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(statement, parameters)
        return cursor.fetchall()
    finally:
        connection.close()


def fetch_one(statement, parameters=()):
    rows = fetch_all(statement, parameters)
    return rows[0] if rows else None
