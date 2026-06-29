from pathlib import Path
from db import conectar

sql = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")


con = conectar()
with con, con.cursor() as cur:
    cur.execute(sql)
con.close()
print("Schema aplicado ✅")