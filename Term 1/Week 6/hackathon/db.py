import sqlite3
import time
import config

def connect(path=None):
    con = sqlite3.connect(str(path or config.DB_PATH), timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS posts (
      uri TEXT PRIMARY KEY, text TEXT, permalink TEXT, created_utc INTEGER,
      collected_utc INTEGER, label TEXT, p_neg REAL, p_neu REAL, p_pos REAL, score REAL);
    CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, started INTEGER, heartbeat INTEGER, ended INTEGER);
    CREATE TABLE IF NOT EXISTS events (time INTEGER, detail TEXT);
    """)
    con.commit()
    return con

def meta(con, key):
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None

def checkpoint(con, cursor):
    con.execute("INSERT OR REPLACE INTO meta VALUES ('cursor', ?)", (str(cursor),))
    con.commit()

def save(con, row):
    con.execute("""INSERT OR REPLACE INTO posts VALUES
    (:uri,:text,:permalink,:created_utc,:collected_utc,:label,:p_neg,:p_neu,:p_pos,:score)""", row)
    con.commit()

def event(con, detail):
    con.execute("INSERT INTO events VALUES (?,?)", (int(time.time()), detail))
    con.commit()
