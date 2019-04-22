import sqlite3
import os
import psycopg2
import psycopg2.extras
import urllib.parse

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DemocracyDB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()
        # self.connection = sqlite3.connect("democracy_db.db")
        # self.connection.row_factory = dict_factory
        # self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createGovernorTable(self):
        self.cursor.execute(
        "CREATE TABLE IF NOT EXISTS governors (id INTEGER PRIMARY KEY, name TEXT, duties TEXT)"
        )
        self.connection.commit()
        return

    def createGovernorDuty(self, name, duty):
        t = (name, duty)
        self.cursor.execute(
            "INSERT INTO governors(name, duties) VALUES(%s, %s)", t)
        self.connection.commit()
        return

    def updateDuty(self, name, duty, id):
        t = (name, duty, id)
        sql = "UPDATE governors SET name=%s, duties=%s WHERE id=%s"
        self.cursor.execute(sql, t)
        self.connection.commit()
        return self.cursor.rowcount

    def getAllGovernors(self):
        self.cursor.execute("SELECT * FROM governors")
        return self.cursor.fetchall()

    def getGovernorsDuties(self, id):
        sql = "SELECT name, duties FROM governors WHERE id=%s"
        self.cursor.execute(sql, [id])
        return self.cursor.fetchone()

    def deleteGovernorDuty(self, id):
        sql = "DELETE FROM governors WHERE id=%s"
        print("id is ", id)
        self.cursor.execute(sql, [id])
        self.connection.commit()
        return self.cursor.rowcount
