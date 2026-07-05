"""Run a SQL file against DATABASE_URL. Usage: python scripts/run-sql.py <file.sql>"""
import os
import sys

import psycopg2

sql = open(sys.argv[1], encoding="utf-8").read()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(sql)
conn.close()
print(f"OK: executed {sys.argv[1]}")
