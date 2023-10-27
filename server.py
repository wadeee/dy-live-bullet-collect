import asyncio
import json

import aiohttp
# The extra strict mypy settings are here to help test that `Application[AppKey()]`
# syntax is working correctly. A regression will cause mypy to raise an error.
# mypy: disallow-any-expr, disallow-any-unimported, disallow-subclassing-any

import os
from typing import List, Union

from aiohttp import web

from douyin import Douyin, DouyinMessage


class Client:
    def __init__(self, ws: web.WebSocketResponse):
        self.room_id = None
        self.ws = ws
        self.dy = None
        pass

    async def set_room_id(self, room_id: str):
        self.room_id = room_id

        url = f"https://live.douyin.com/{room_id}"
        dy = Douyin(url, on_message=self.on_message)
        await dy.connect_web_socket()
        self.dy = dy

    def close(self):
        self.dy.ws_conn.close()
        pass

    async def on_message(self, message: DouyinMessage):
        await self.ws.send_json({'ddd':'ddddd'})



async def on_message(client: Client, message: str):
    msg = json.loads(message)
    if 'type' not in msg:
        return
    if msg['type'] == 'room_id':
        await client.set_room_id(msg['data'])


async def wshandler(request: web.Request) -> Union[web.WebSocketResponse, web.Response]:
    ws = web.WebSocketResponse()
    await ws.prepare(request)  # 等待websocket连接

    client = Client(ws)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:  # type: ignore[misc]
            if msg.data == 'close':  # type: ignore[misc]
                await ws.close()
            else:
                await on_message(client, msg.data)  # type: ignore[misc]
        elif msg.type == aiohttp.WSMsgType.ERROR:  # type: ignore[misc]
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')
    await client.close()
    return ws


async def on_shutdown(app: web.Application) -> None:
    for ws in sockets:
        await ws.close()


sockets: List[web.WebSocketResponse] = []


def init() -> web.Application:
    app = web.Application()
    app.router.add_get("/", wshandler)
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init())
