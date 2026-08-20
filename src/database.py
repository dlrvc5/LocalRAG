import sqlite3

connection=sqlite3.connect("data/rag.db")

cursor= connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    text TEXT,

    embedding TEXT

)
""")

connection.commit()
connection.close()
print("Veritabanı oluşturuldu.")