import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect(".databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM id7-tusers")
    con.close()
    return cur

