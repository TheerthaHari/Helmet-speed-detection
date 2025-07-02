import sqlite3

def init_db():
    conn= sqlite3.connect('violations.db')
    c= conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS violations(id INTEGER PRIMARY KEY AUTOINCREMENT,track_id INTEGER,timestamp TEXT,violation_type TEXT, license_plate TEXT,speed REAL,img_base64 Text)")
    conn.commit()
    conn.close()

def log_violation(track_id,timestamp, violation_type,license_plate,speed,img_base64):
    conn=sqlite3.connect('violations.db')
    c= conn.cursor()
    c.execute("INSERT INTO violations(track_id,timestamp,violation_type,license_plate,speed,img_base64)VALUES(?,?,?,?,?,?)",(track_id,timestamp,violation_type,license_plate,speed,img_base64))
    conn.commit()
    conn.close()
    