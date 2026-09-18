import asyncio
import websockets


async def main():

    uri = "ws://127.0.0.1:8000/ws/text"

    async with websockets.connect(uri) as websocket:

        print("Connected!")

        await websocket.send("Hello WebSocket")

        while True:

            message = await websocket.recv()

            print(message, end="", flush=True)

            if message == "[DONE]":
                break


asyncio.run(main())