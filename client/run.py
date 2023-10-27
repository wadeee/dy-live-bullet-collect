import asyncio
import aiohttp

# 设置连接的host地址
SERVER_URL = 'http://localhost:8080'

class MessageSender:
    def __init__(self):
        self.session = None
        self.ws = None

    async def connect_to_server(self):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(SERVER_URL)
        print("已连接到服务器")

    async def send_message(self, message):
        await self.ws.send_json({
            'type': 'room_id',
            'data': message
        })

        msg = await self.ws.receive()
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            print("接收到服务器响应：", msg.data)
        elif msg.type == aiohttp.WSMsgType.CLOSED:
            print("连接已关闭")
            await self.close_connection()
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print("连接发生错误")
            await self.close_connection()

    async def close_connection(self):
        await self.ws.close()
        await self.session.close()
        print("连接已关闭")

async def main():
    sender = MessageSender()
    await sender.connect_to_server()

    while True:
        message = input("请输入要发送给服务器的消息（输入exit退出）：")
        if message == "exit":
            break

        await sender.send_message(message)

    await sender.close_connection()

asyncio.run(main())
