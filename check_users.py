import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv('d:\\herman_musik\\backend\\.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'herman_musik')
)

cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

print('Users dalam database:')
for user in users:
    print(f"  - {user['username']} ({user['role']}) - {user['email']}")

cursor.close()
conn.close()
