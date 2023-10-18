import json

import mysql.connector  # pip install mysql-connector-python


def dump_table(table, parent_id, level):
    for id in sorted(table.keys()):
        if table[id]["parentId"] == parent_id:
            print("  " * level, end="")
            print(json.dumps(table[id], ensure_ascii=False))
            dump_table(table, parent_id=table[id]["id"], level=level + 1)


config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "ocaz_terminology",
}


connection = mysql.connector.connect(**config)
cursor = connection.cursor()

table = {}
cursor.execute(
    "SELECT id, parent_id, created_at, updated_at, representative_ja, representative_en FROM terms ORDER BY id ASC;"
)
for (
    id,
    parent_id,
    created_at,
    updated_at,
    representative_ja,
    representative_en,
) in cursor.fetchall():
    record = {
        "id": id,
        "parentId": parent_id,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "representative": {
            "ja": representative_ja,
            "en": representative_en,
        },
    }
    table[record["id"]] = record

dump_table(table, parent_id=None, level=0)
