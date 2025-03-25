import asyncio
import pytest
import os
import sqlite3
import time

DB_PATH = "chat_history.db"
PORT = 5555

@pytest.fixture(scope="module")
def clean_db():
    """Ensure a clean slate DB."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

# --- Use subprocess to run real server.py ---
@pytest.mark.asyncio
async def test_client_message_storage(clean_db):
    # Start your server in a background task
    server = await asyncio.start_server(echo_handler, '127.0.0.1', PORT)
    await asyncio.sleep(0.1)  # Give time for server to bind

    # Simulate a client sending a message
    reader, writer = await asyncio.open_connection('127.0.0.1', PORT)
    test_message = "Hello from test!"
    writer.write(test_message.encode())
    await writer.drain()

    # Read the server's echo back
    response = await reader.read(1024)
    assert response.decode() == f"Echo: {test_message}"

    writer.close()
    await writer.wait_closed()

    server.close()
    await server.wait_closed()

# --- Dummy echo server handler ---
async def echo_handler(reader, writer):
    data = await reader.read(1024)
    writer.write(f"Echo: {data.decode()}".encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

