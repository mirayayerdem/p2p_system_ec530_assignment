import asyncio
import sqlite3
async def receive_messages(reader,cursor,conn):
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode().strip()
            # Print incoming message (with a newline to avoid clashing with your prompt)
            print("\n" + message)
            
            # Try to parse the message in the format "Sender: message"
            if ": " in message:
                sender, msg = message.split(": ", 1)
                cursor.execute("INSERT INTO messages (sender,receiver, message) VALUES (?, ?,?)", (sender, 'Me', msg))
                conn.commit()
            else:
                sender, msg = "System", message
            

        except asyncio.CancelledError:
            break
async def send_messages(writer,cursor,conn):
    while True:
        try:
            
            # Use asyncio.to_thread to not block the event loop while waiting for user input.
            line = await asyncio.to_thread(input,'Enter target and message (e.g., kiki-Hello!):')
            writer.write(f"{line}\n".encode())
            await writer.drain()
            parts = line.split("-", 1)
            print(parts)
            if len(parts) >1:
                target, msg = parts[0], parts[1]

                # You can add validation here if needed.

                cursor.execute("INSERT INTO messages (sender, receiver,message) VALUES (?, ?,?)", ('Me',target, msg))
                conn.commit()
        except asyncio.CancelledError:
            break
async def start_client():

    server_ip = input("Enter server IP (e.g., 127.0.0.1): ")
    port = input("Enter server port (e.g., 5555): ")
    try:
        port = int(port)
    except ValueError:
        print("Invalid port number.")
        return

    reader, writer = await asyncio.open_connection(server_ip, port)
    print('Connection to server is successful')
  # Username setup
    welcome = await reader.read(1024)
    print(welcome.decode(), end='')
    username = input()
    writer.write(f"{username}\n".encode())
    await writer.drain()
    conn = sqlite3.connect(f"chat_history_{username}.db")
    cursor = conn.cursor()
    #creation of db
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    receive_task = asyncio.create_task(receive_messages(reader, cursor, conn))
    send_task = asyncio.create_task(send_messages(writer,cursor,conn))

    # Wait until one of the tasks completes (or you can use a different exit strategy).
    done, pending = await asyncio.wait(
        [receive_task, send_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel any pending tasks.
    for task in pending:
        task.cancel()

    print('Closing connection')
    writer.close()
    await writer.wait_closed()
    conn.close()
asyncio.run(start_client())
    
