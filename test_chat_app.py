import asyncio
import pytest
import sqlite3
from unittest.mock import AsyncMock, patch

from main import handle_client  # adjust if your file is named differently

@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Updated schema for `users` table
    cursor.execute("""
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            ip TEXT,
            port INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE offline_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            target TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    yield conn, cursor
    conn.close()

@pytest.mark.asyncio(scope="function")
async def test_handle_client_new_user(monkeypatch, in_memory_db):
    conn, cursor = in_memory_db

    # Mock reader and writer
    from unittest.mock import AsyncMock, MagicMock

    reader = AsyncMock()
    writer = MagicMock()
    writer.write = AsyncMock()
    writer.drain = AsyncMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()

    mock_ip = '192.168.1.5'
    mock_port = 56789
    writer.get_extra_info.return_value = (mock_ip, mock_port)

    # Simulate peer info
    mock_ip = '192.168.1.5'
    mock_port = 56789
    writer.get_extra_info.return_value = (mock_ip, mock_port)

    # Simulate username input and disconnect
    reader.read = AsyncMock(side_effect=[
        b'testuser\n',  # username input
        b''             # simulate disconnect
    ])

    # Patch global vars in server module
    monkeypatch.setitem(__import__('main').__dict__, 'db_conn', conn)
    monkeypatch.setitem(__import__('main').__dict__, 'db_cursor', cursor)
    monkeypatch.setitem(__import__('main').__dict__, 'clients', {})

    await handle_client(reader, writer)

    # Verify the user was saved with correct IP and port
    cursor.execute("SELECT username, ip, port FROM users WHERE username = 'testuser'")
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == 'testuser'
    assert result[1] == mock_ip
    assert result[2] == mock_port