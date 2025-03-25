import asyncio

async def receive_from_client(reader, address):
    while True:
        data = await reader.read(1024)
        if not data:
            print(f"Client {address} disconnected.")
            break
        print(f"\nClient {address}: {data.decode()}")

async def send_to_client(writer, address):
    while True:
        try:
            message = await asyncio.to_thread(input, "Server: ")
            writer.write(message.encode())
            await writer.drain()
        except asyncio.CancelledError:
            break
async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    print(f"Connection from {address}")

    recv_task = asyncio.create_task(receive_from_client(reader, address))
    send_task = asyncio.create_task(send_to_client(writer, address))

    # Wait until either task completes
    done, pending = await asyncio.wait(
        [recv_task, send_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel remaining tasks and clean up
    for task in pending:
        task.cancel()

    writer.close()
    await writer.wait_closed()
    print(f"🔒 Closed connection - {address}")
   
async def start_server():
    server = await asyncio.start_server(handle_client,'0.0.0.0', 5555)
    address = server.sockets[0].getsockname()
    print(f'Server running at this address {address}')

    async with server:
        await server.serve_forever()
asyncio.run(start_server())

