# p2p_system_ec530_assignment

# Asyncio Chat Application with Offline Messaging
This project is a simple terminal-based chat application built using Python's `asyncio` and `sqlite3` modules. It supports real-time communication between clients, with offline message delivery and local message history storage per user.

---

## Features

- Real-time messaging between connected users  
- Offline message storage and delivery on next login  
- Local SQLite database for message history (per client)  
- Server-side database for user tracking and offline messages  
- Client book display on login  
- Async handling of multiple clients

---

## Requirements

- Python 3.8+
- No external dependencies

---

## File Structure

```
.
├── client.py        # Code for the client-side chat interface
├── server.py        # Server-side code that handles all client communication
├── README.md        # You're here!
```

---

## Getting Started

### 1. Start the Server

Run the following command on the host machine (or your local machine if testing locally):

```bash
python server.py
```

The server listens on `0.0.0.0:5555` by default.

### 2. Start the Client

On any machine (or the same machine for local testing), run:

```bash
python client.py
```

You'll be prompted to:

- Enter the server IP (e.g., `127.0.0.1`)
- Enter the server port (default: `5555`)
- Enter a unique username

Once connected, you'll see:

- A welcome message
- The list of registered users
- Any offline messages if applicable

---

## Sending Messages

To send a message, follow this format:

```
<target_username>-<message>
```

Example:
```
alice-Hey there!
```
Please tap 'Return' key to write a message after receiving a message.

### Notes:
- If the target is online, they receive the message instantly.
- If the target is offline, the message is stored in the server database and delivered when they next connect.
- All messages are logged locally on the client side (`chat_history_<username>.db`).

---

## Database Info

### Server Database (`server.db`)
- `users`: Stores usernames and their last known IP/port.
- `offline_messages`: Queues messages for offline delivery.

### Client Database (`chat_history_<username>.db`)
- `messages`: Logs sent and received messages for that user.
