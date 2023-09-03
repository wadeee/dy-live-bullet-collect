import gzip
import json
import logging
import re
import time
import urllib.parse
from datetime import datetime

import requests
import websocket

import config
from protobuf import dy_pb2


class Douyin:

    def __init__(self, url):
        self.ws_conn = None
        self.url = url

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
        re_pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
        re_obj = re.compile(re_pattern)
        match = re_obj.search(res_origin_text)
        if match:
            try:
                match_text = match.group(1)
                res_text = urllib.parse.unquote(match_text)
                app_data = json.loads(res_text)
                app_json = app_data.get("app")
                initial_state_json = app_json.get("initialState")
                room_store_json = initial_state_json.get("roomStore")
                live_room_id = room_store_json.get("roomInfo").get("roomId")
                live_room_title = room_store_json.get("roomInfo").get("room").get("title")
                self.room_info = {
                    'url': self.url,
                    'ttwid': ttwid,
                    'room_store': room_store_json,
                    'room_id': live_room_id,
                    'room_title': live_room_title,
                }
            except Exception:
                self.room_info = None
        else:
            self.room_info = None

    def connect_web_socket(self):
        self._get_room_info()
        if self.room_info is None:
            logging.error(f"获取直播间({self.url})信息失败")
            return

        ws_url = config.content['ws']['origin_url'].replace("%s", self.room_info.get('room_id'))
        headers = {
            'cookie': 'ttwid=' + self.room_info.get('ttwid'),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'
        }

        websocket.enableTrace(False)
        self.ws_conn = websocket.WebSocketApp(ws_url,
                                              header=headers,
                                              on_message=self._on_message,
                                              on_open=self._on_open,
                                              on_error=self._on_error,
                                              on_close=self._on_close)

        self.ws_conn.run_forever(reconnect=1)

    def _send_ask(self, log_id, internal_ext):
        ack_pack = dy_pb2.PushFrame()
        ack_pack.logId = log_id
        ack_pack.payloadType = internal_ext

        data = ack_pack.SerializeToString()
        self.ws_conn.send(data, opcode=websocket.ABNF.OPCODE_BINARY)

    def _on_message(self, ws, message):
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
                    self._parse_chat_msg(msg.payload)
                case "WebcastGiftMessage":
                    self._parse_gift_msg(msg.payload)
                case "WebcastLikeMessage":
                    self._parse_like_msg(msg.payload)
                case "WebcastMemberMessage":
                    self._parse_member_msg(msg.payload)
                # case 'WebcastInRoomBannerMessage':
                # case 'WebcastRoomRankMessage':
                # case 'WebcastRoomDataSyncMessage':
                # case _:

    @staticmethod
    def _on_error(ws, error):
        logging.error(error)

    @staticmethod
    def _on_close(ws, close_status_code, close_msg):
        logging.info("Websocket closed")

    @staticmethod
    def _on_open(ws):
        logging.info("Websocket opened")

    @staticmethod
    def _parse_chat_msg(payload):
        payload_pack = dy_pb2.ChatMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload_pack.eventTime))
        user_name = payload_pack.user.nickName
        content = payload_pack.content
        print(f"{formatted_time} [弹幕] {user_name}: {content}")

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
