import gzip
import json
import logging
import re
import time
from datetime import datetime

import requests
import websockets
import config
from protobuf import dy_pb2


class DouyinMessage:
    def __init__(self, time: str, type: str, user_name: str, content: str):
        self.time = time
        self.type = type
        self.user_name = user_name
        self.content = content



class Douyin:

    def __init__(self, url, on_message):
        self.ws_conn = None
        self.url = url
        self.room_info = None
        self.__on_message__ = on_message

    def _get_room_info(self):
        payload = {}
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
            'cookie': '__ac_nonce=0638733a400869171be51',
        }

        proxies = dict(http="", https="")

        response = requests.get(self.url, headers=headers, data=payload, proxies=proxies)
        res_cookies = response.cookies
        ttwid = res_cookies.get_dict().get("ttwid")
        res_origin_text = response.text
        re_pattern = config.content['douyin']['re_pattern']
        re_obj = re.compile(re_pattern)
        matches = re_obj.findall(res_origin_text)
        for match_text in matches:
            try:
                match_json_text = json.loads(f'"{match_text}"')
                match_json = json.loads(match_json_text)
                if match_json.get('state') is None:
                    continue
                room_id = match_json.get('state').get('roomStore').get('roomInfo').get('roomId')
                room_title = match_json.get('state').get('roomStore').get('roomInfo').get('room').get('title')
                room_user_count = match_json.get('state').get('roomStore').get('roomInfo').get('room').get(
                    'user_count_str')
                unique_id = match_json.get('state').get('userStore').get('odin').get('user_unique_id')
                avatar = match_json.get('state').get('roomStore').get('roomInfo').get('anchor').get('avatar_thumb').get(
                    'url_list')[0]
                self.room_info = {
                    'url': self.url,
                    'ttwid': ttwid,
                    'room_id': room_id,
                    'room_title': room_title,
                    'room_user_count': room_user_count,
                    'unique_id': unique_id,
                    'avatar': avatar,
                }
            except Exception:
                self.room_info = None

    async def connect_web_socket(self):
        self._get_room_info()
        if self.room_info is None:
            logging.error(f"获取直播间({self.url})信息失败")
            return

        now = str(time.time_ns() // 1000000)
        ws_url = config.content['douyin']['ws_origin_url'].replace('${room_id}', self.room_info.get('room_id')).replace(
            '${unique_id}', self.room_info.get('unique_id')).replace('${now}', now)
        headers = {
            'cookie': 'ttwid=' + self.room_info.get('ttwid'),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'
        }
        try:
            # print("ws_url", ws_url)
            async with websockets.connect(ws_url, extra_headers=headers) as ws_conn:
                self.ws_conn = ws_conn
                await self._on_open(self.ws_conn)
                async for message in ws_conn:
                    await self._on_message(self.ws_conn,message)
        except websockets.ConnectionClosedError as e:
            await self._on_close(e,self.ws_conn,'close')
        except Exception as e:
            await self._on_error(e,self.ws_conn)
                
  
    def _send_ask(self, log_id, internal_ext):
        ack_pack = dy_pb2.PushFrame()
        ack_pack.logId = log_id
        ack_pack.payloadType = internal_ext

        data = ack_pack.SerializeToString()
        # self.ws_conn.send(data, opcode=websocket.ABNF.OPCODE_BINARY)

    async def _on_message(self, ws, message):
        msg_pack = dy_pb2.PushFrame()
        msg_pack.ParseFromString(message)
        decompressed_payload = gzip.decompress(msg_pack.payload)
        payload_package = dy_pb2.Response()
        payload_package.ParseFromString(decompressed_payload)
        if payload_package.needAck:
            self._send_ask(msg_pack.logId, payload_package.internalExt)
        for msg in payload_package.messagesList:
            match msg.method:
                case 'WebcastChatMessage':
                    await self._parse_chat_msg(msg.payload)
      

    @staticmethod
    async def _on_error(ws, error):
        logging.error(error)

    @staticmethod
    async def _on_close(ws, close_status_code, close_msg):
        logging.info("Websocket closed")

    @staticmethod
    async def _on_open(ws):
        logging.info("Websocket opened")

    async def _parse_chat_msg(self, payload):
        payload_pack = dy_pb2.ChatMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload_pack.eventTime))
        user_name = payload_pack.user.nickName
        content = payload_pack.content
        print(f"{formatted_time} [弹幕] {user_name}: {content}")
        message = DouyinMessage(formatted_time, '弹幕', user_name, content)
        await self.__on_message__(message)

    @staticmethod
    def _parse_gift_msg(payload):
        payload_pack = dy_pb2.GiftMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName
        gift_name = payload_pack.gift.name
        gift_cnt = payload_pack.comboCount
        print(f"{formatted_time} [礼物] {user_name}: {gift_name} * {gift_cnt}")

    @staticmethod
    def _parse_like_msg(payload):
        payload_pack = dy_pb2.LikeMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName
        like_cnt = payload_pack.count
        print(f"{formatted_time} [点赞] {user_name}: 点赞 * {like_cnt}")

    @staticmethod
    def _parse_member_msg(payload):
        payload_pack = dy_pb2.MemberMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName
        print(f"{formatted_time} [入场] {user_name} 进入直播间")
