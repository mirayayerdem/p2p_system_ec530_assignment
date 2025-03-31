import asyncio
import sqlite3

clients = {}

# Global dictionary to hold online clients: username -> writer
clients = {}

# Set up the persistent database connection and create tables if they don't exist.
db_conn = sqlite3.connect("server.db")
db_cursor = db_conn.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        ip TEXT,
        port INTEGER
        
    )
""")
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS offline_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        target TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
db_conn.commit()


async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    writer.write("Enter your username: ".encode())
    await writer.drain()
    username = (await reader.read(1024)).decode().strip()
    clients[username] = writer
    ip, port = writer.get_extra_info('peername')
    db_cursor.execute(
    "INSERT OR REPLACE INTO users (username, ip, port) VALUES (?, ?, ?)",
    (username, ip, port)
)
    db_conn.commit()
    print(f"{username} connected from {address}")
    db_cursor.execute("SELECT username FROM users")
    all_users = [row[0] for row in db_cursor.fetchall()]
    writer.write(f"Client book => {', '.join(all_users)}\n".encode())
    await writer.drain()
    db_cursor.execute("SELECT id, sender, message,timestamp FROM offline_messages WHERE target = ?", (username,))
    offline_msgs = db_cursor.fetchall()
    if offline_msgs:
        writer.write("You have offline messages:\n".encode())
        for msg in offline_msgs:
            msg_id, sender, message, timestamp= msg
            writer.write(f"{sender}: {message} ({timestamp})\n".encode())
        await writer.drain()
        # Remove delivered offline messages.
        db_cursor.execute("DELETE FROM offline_messages WHERE target = ?", (username,))
        db_conn.commit()
    try:
            while True:
                client_list = ", ".join(user for user in clients if user != username)
                writer.write(f"\nUsers online=> {client_list}\n".encode())
                await writer.drain()
                # Prompt the client for a combined input: <target> <message>
                writer.write("Enter target and message (e.g., kiki-Hello!): ".encode())
                await writer.drain()

                data = await reader.read(1024)
                if not data:
                    break
                line = data.decode().strip()
                if not line:
                    continue  # skip empty inputs

                # Split into target and message using the first space as delimiter
                parts = line.split("-", 1)
                if len(parts) < 2:
                    writer.write("Format error. Please enter: <target>-<message>\n".encode())
                    await writer.drain()
                    continue

                target, msg = parts[0], parts[1]
                if target in clients:
                    target_writer = clients[target]
                    target_writer.write(f"\n{username}: {msg}\n".encode())
                    await target_writer.drain()
                elif target in all_users:
                    # If the target is offline, store the message for later delivery.
                    db_cursor.execute("INSERT INTO offline_messages (sender, target, message) VALUES (?, ?, ?)",
                                    (username, target, msg))
                    db_conn.commit()
                    writer.write(f"User '{target}' is offline. Message stored.\n".encode())
                    await writer.drain()
                else:
                    writer.write("User not found.\n".encode())
                    await writer.drain()

    except (asyncio.IncompleteReadError, ConnectionResetError):
            print(f"{username} disconnected.")
    finally:
            del clients[username]
            writer.close()
            await writer.wait_closed()

    
    
 
async def start_server():
    server = await asyncio.start_server(handle_client,'0.0.0.0', 5555) #all addresses on the local machine 
    address = server.sockets[0].getsockname()
    print(f'Server running at this address {address}')

    async with server:
        await server.serve_forever()
if __name__ == "__main__":
    asyncio.run(start_server())
