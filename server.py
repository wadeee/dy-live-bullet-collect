import asyncio
import json

import aiohttp
# The extra strict mypy settings are here to help test that `Application[AppKey()]`
# syntax is working correctly. A regression will cause mypy to raise an error.
# mypy: disallow-any-expr, disallow-any-unimported, disallow-subclassing-any
import inspect
import ctypes


from typing import List, Union

from aiohttp import web

from douyin import Douyin, DouyinMessage



sockets: List[web.WebSocketResponse] = []
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
        self.dy = dy
        asyncio.create_task(dy.connect_web_socket())

    async def close(self):
        await  self.dy.ws_conn.close()
        pass

    
    async def on_message(self, message: DouyinMessage):
        await self.ws.send_json(message.__dict__)



async def on_message(client: Client, message: str):
    print(message)




async def wshandler(request: web.Request) -> Union[web.WebSocketResponse, web.Response]:
    ws = web.WebSocketResponse()
    await ws.prepare(request)  # 等待websocket连接
    sockets.append(ws)
    client = Client(ws)
    id= request.query['id']
    await client.set_room_id(id)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:  # type: ignore[misc]
            info =json.loads(msg.data)
            if  info['type'] == "control" and  info['data']=="close":  # type: ignore[misc]
                # print(dir(client))
                await client.dy.ws_conn.close()
                await ws.close()
            elif  info['type'] == "msg":
                print(info)
                await on_message(client,info['data'])
            else:
                # 待定
                print(info)
        elif msg.type == aiohttp.WSMsgType.ERROR:  # type: ignore[misc]
            print('ws connection closed with exception %s' %
                  ws.exception())
    


    print('websocket connection closed')
    await client.close()
    return ws


async def on_shutdown(app: web.WebSocketResponse) -> None:
    for ws in sockets:
        await ws.close()





def init() -> web.Application:
    app = web.Application()
    # 匹配 room id
    app.router.add_get("/id", wshandler)
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init())
