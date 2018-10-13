import sqlite3

def getConnection(db):
    database=db
    try:
        conn=sqlite3.connect(database)
        cur=conn.cursor()
        return (conn,cur)
    except Error as e:
        print (e)
        conn.close()
    finally:
        pass
