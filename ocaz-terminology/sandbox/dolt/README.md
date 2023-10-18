# dolt

Doltの検証コードなど。

```sh
dolt sql-server --user=root
dolt sql-client
python tool/dump.py > dump.jsonl
python tool/dump_tree.py > dump_tree.txt
python tool/add.py < in.tsv
```

```sql
SHOW DATABASES;
USE ocaz_terminology;
SHOW TABLES;
SELECT * FROM terms;
SELECT * FROM synonyms;
```
