import sqlite3

conn = sqlite3.connect("/Users/mirayrdm/Documents/Courses/EC530/p2p_system_ec530_assignment/chat_history.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM messages")
rows = cursor.fetchall()

if not rows:
    print("⚠️ No messages found in database.")
else:
    for row in rows:
        print(row)

conn.close()