import sqlite3
import json
from passlib.hash import pbkdf2_sha256
import os
import psycopg2
import psycopg2.extras
import urllib.parse

class UserDB:
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

    def __del__(self):
        self.connection.close()

    def hashPW(self, pw):
        myhash = pbkdf2_sha256.hash(pw)
        return myhash

    def verifyPassword(self, pw, myhash):
        return pbkdf2_sha256.verify(pw, myhash)

    def validateEmailUniqueness(self, email):
        sql = "SELECT user_id FROM user WHERE email=%s"
        self.cursor.execute(sql, [email])
        return self.cursor.fetchone()

    def getUserByEmail(self, email):
        sql = "SELECT user_id, hash FROM user WHERE email=%s"
        self.cursor.execute(sql, [email])
        return self.cursor.fetchone()

    def createNewUser(self, f_name, l_name, email, password):
        result = self.validateEmailUniqueness(email)
        print(json.dumps(result))
        if json.dumps(result) != "null":
            return False
        myhash = self.hashPW(password)
        t = (f_name, l_name, email, myhash)
        self.cursor.execute(
            "INSERT INTO user(first_name, last_name, email, hash) VALUES(%s, %s, %s, %s)", t)
        self.connection.commit()
        return True

    def createUserTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user (user_id serial PRIMARY KEY,first_name text not null,last_name text not null,email text not null unique,hash text not null)")
        self.connection.commit()
        return

