import random
from datetime import datetime

import mysql.connector  # pip install mysql-connector-python


def make_random_id():
    return f"{random.randint(0, 2**31 - 1):08x}"


def get_id_from_representative_ja(cursor, representative_ja, parent_id=None):
    if parent_id is None:
        cursor.execute(
            "SELECT id, representative_ja FROM terms WHERE parent_id IS NULL AND representative_ja = %(representative_ja)s ORDER BY id ASC;",
            {"representative_ja": term},
        )
        for id, representative_ja in cursor.fetchall():
            return {"id": id, "representative_ja": representative_ja}
        return None
    else:
        cursor.execute(
            "SELECT id, representative_ja FROM terms WHERE parent_id = %(parent_id)s AND representative_ja = %(representative_ja)s ORDER BY id ASC;",
            {"parent_id": parent_id, "representative_ja": term},
        )
        for id, representative_ja in cursor.fetchall():
            return {"id": id, "representative_ja": representative_ja}
        return None


def insert_term(
    cursor, id, parent_id, created_at, updated_at, representative_ja, representative_en
):
    cursor.execute(
        "INSERT INTO terms(id, parent_id, created_at, updated_at, representative_ja, representative_en) VALUES (%(id)s, %(parent_id)s, %(created_at)s, %(updated_at)s, %(representative_ja)s, %(representative_en)s)",
        {
            "id": id,
            "parent_id": parent_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "representative_ja": representative_ja,
            "representative_en": representative_en,
        },
    )


config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "ocaz_terminology",
}


connection = mysql.connector.connect(**config)
cursor = connection.cursor()

records = [["出演者", "女性", "役割", "上司"]]

for terms in records:
    print(terms)
    parent_id = None
    for term in terms:
        print((parent_id, term))
        record = get_id_from_representative_ja(
            cursor=cursor, representative_ja=term, parent_id=parent_id
        )
        print(record)
        if record is None:
            new_id = make_random_id()
            now = int(datetime.now().timestamp())
            print(new_id)
            insert_term(
                cursor,
                id=new_id,
                parent_id=parent_id,
                created_at=now,
                updated_at=now,
                representative_ja=term,
                representative_en=None,
            )
            parent_id = new_id
        else:
            parent_id = record["id"]

cursor.execute("SELECT * FROM dolt_status;")
print(cursor.fetchall())
cursor.execute("CALL dolt_add('terms');")
print(cursor.fetchall())
cursor.execute("CALL dolt_commit('-m', 'Add terms');")
print(cursor.fetchall())
