import os
import sqlite3


DATABASE_PATH = "database/stock_analysis.db"


def get_connection():
    """
    Create and return a SQLite database connection.
    """

    database_directory = os.path.dirname(DATABASE_PATH)

    if database_directory:
        os.makedirs(
            database_directory,
            exist_ok=True
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def execute_query(query, parameters=()):
    """
    Execute a single INSERT, UPDATE, or DELETE query.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            query,
            parameters
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def fetch_all(query, parameters=()):
    """
    Execute a SELECT query and return all rows.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            query,
            parameters
        )

        return cursor.fetchall()

    finally:
        connection.close()


def fetch_one(query, parameters=()):
    """
    Execute a SELECT query and return one row.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            query,
            parameters
        )

        return cursor.fetchone()

    finally:
        connection.close()