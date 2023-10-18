from datetime import datetime

import mysql.connector  # pip install mysql-connector-python

config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "ocaz_terminology",
}


connection = mysql.connector.connect(**config)
connection.ping(reconnect=True)
print(connection.is_connected())

cursor = connection.cursor()

insert_sql = "INSERT INTO terms(id, parent_id, created_at, updated_at, representative_ja, representative_en) VALUES (%(id)s, %(parent_id)s, %(created_at)s, %(updated_at)s, %(representative_ja)s, %(representative_en)s)"

now = int(datetime.now().timestamp())
cursor.execute(
    insert_sql,
    {
        "id": "240f7f86",
        "parent_id": None,
        "created_at": now,
        "updated_at": now,
        "representative_ja": "出演者",
        "representative_en": "Actor",
    },
)

cursor.execute("SELECT * FROM terms;")
print(cursor.fetchall())

cursor.execute("SELECT * FROM dolt_status;")
print(cursor.fetchall())

cursor.execute("CALL dolt_add('terms');")
print(cursor.fetchall())

cursor.execute("SELECT * FROM dolt_status;")
print(cursor.fetchall())

cursor.execute("CALL dolt_commit('-m', 'Add terms');")
print(cursor.fetchall())

cursor.close()
connection.close()
