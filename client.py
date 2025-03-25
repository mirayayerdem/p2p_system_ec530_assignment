import asyncio
import sqlite3
async def receive_messages(reader,cursor,conn):
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break
            print(f'Server: {data.decode()}')
            data = data.decode()
            cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", ("Friend", data)) #it will change later
            conn.commit()

        except asyncio.CancelledError:
            break
async def send_messages(writer,cursor,conn):
    while True:
        try:
            data = await asyncio.to_thread(input,'Client: ')
            if data.lower() == "exit":
                break
            writer.write(data.encode())
            await writer.drain()
            cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", ("Me", data))
            conn.commit()
        except asyncio.CancelledError:
            break

async def start_client():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    #creation of db
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    reader,writer = await asyncio.open_connection('127.0.0.1', 5555)
    print('Connection to server is successful')

    recv_task = asyncio.create_task(receive_messages(reader, cursor, conn))
    send_task = asyncio.create_task(send_messages(writer,cursor,conn))

    # Wait until one of them completes
    done, pending = await asyncio.wait(
        [recv_task, send_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    print('Closing connection')
    writer.close()
    await writer.wait_closed()
    conn.close()

asyncio.run(start_client())
    
