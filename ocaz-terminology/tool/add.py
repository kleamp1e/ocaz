import random
import sys
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


def delete_all_synonyms(cursor, id):
    cursor.execute("DELETE FROM synonyms WHERE id = %(id)s;")


def add_synonym(cursor, id, synonym_ja, synonym_en):
    cursor.execute(
        "INSERT INTO synonyms(id, synonym_ja, synonym_en) VALUES(%(id)s, %(synonym_ja)s, %(synonym_en)s);",
        {
            "id": id,
            "synonym_ja": synonym_ja,
            "synonym_en": synonym_en,
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

for line in sys.stdin.readlines():
    terms = line.strip().split("\t")
    print(terms)
    parent_id = None
    for term in terms:
        first_term, *rest_terms = term.split("|")
        print((parent_id, term))
        record = get_id_from_representative_ja(
            cursor=cursor, representative_ja=first_term, parent_id=parent_id
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
                representative_ja=first_term,
                representative_en=None,
            )
            current_id = new_id
        else:
            current_id = record["id"]

        print("rest_terms:", rest_terms)
        for rest_term in rest_terms:
            add_synonym(
                cursor=cursor, id=current_id, synonym_ja=rest_term, synonym_en=None
            )

        parent_id = current_id

cursor.execute("CALL dolt_add('terms');")
print(cursor.fetchall())
cursor.execute(
    "CALL dolt_commit('-m', '用語を追加', '--author', 'kleamp1e <kleamp1e@gmail.com>');"
)
print(cursor.fetchall())

"""
cursor.execute("SELECT * FROM dolt_status;")
print(cursor.fetchall())
"""
