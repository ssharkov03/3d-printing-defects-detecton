import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_database(database_name):
    database = database_name

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
    id                     INTEGER       PRIMARY KEY AUTOINCREMENT,
    user_id                VARCHAR (255) NOT NULL,
    status                 BOOLEAN       DEFAULT (TRUE) 
                                         NOT NULL,
    stream                 TEXT,
    notifications_period   INTEGER       DEFAULT (300) 
                                         NOT NULL,
    predictions_since_last INTEGER       DEFAULT (1) 
                                         NOT NULL,
    defects_period         INTEGER       NOT NULL
                                         DEFAULT (30),
    defects_since_last     INTEGER       DEFAULT (1) 
                                         NOT NULL,
    detect_defects         BOOLEAN       NOT NULL
                                         DEFAULT (TRUE),
    defects_mute           BOOLEAN       DEFAULT (FALSE) 
                                         NOT NULL
);
 """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create users table
        create_table(conn, sql_create_users_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")


