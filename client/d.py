import asyncio
import websockets

async def handle_messages(websocket):
    try:
        while True:
            data = await websocket.recv()
            print("Received message:", data)
            if data == 'close':
                break
    except websockets.exceptions.ConnectionClosedError:
        print("WebSocket connection closed")

async def main():
    uri = "http://192.168.180.54:8080/id"
    async with websockets.connect(uri+'?id='+str(785217135756)) as websocket:
        receive_task = asyncio.create_task(handle_messages(websocket))
        await receive_task  # 等待消息处理任务结束

asyncio.run(main())