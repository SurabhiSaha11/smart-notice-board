import os
import time
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
import pymssql

load_dotenv()
url = make_url(os.environ["DATABASE_URL"])

for attempt in range(1, 9):
    try:
        conn = pymssql.connect(
            server=url.host, user=url.username, password=url.password,
            database=url.database, login_timeout=60
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM [user]")
        print("Connected! Users in database:", cur.fetchone()[0])
        conn.close()
        break
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        time.sleep(15)
else:
    print("Could not connect after 8 attempts.")
