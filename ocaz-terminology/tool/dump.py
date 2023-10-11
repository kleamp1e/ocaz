import json

import mysql.connector  # pip install mysql-connector-python

config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "ocaz_terminology",
}


connection = mysql.connector.connect(**config)
cursor = connection.cursor()

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
    print(json.dumps(record,ensure_ascii=False))
