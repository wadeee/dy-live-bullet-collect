import gzip
import json
import logging
import re
import time
import urllib.parse

import requests
import websocket

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
            except Exception as e:
                self.room_info = None
        else:
            self.room_info = None

    def connect_web_socket(self):
        self._get_room_info()
        if self.room_info is None:
            logging.error(f"获取直播间({self.url})信息失败")
            return
        ws_url = (r'wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800'
                  r'&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim'
                  r'|wss_push_room_id:%s|wss_push_did:%s|dim_log_id:202302171547011A160A7BAA76660E13ED|fetch_time'
                  r':1676620021641|seq:1|wss_info:0-1676620021641-0-0|wrds_kvs:WebcastRoomStatsMessage'
                  r'-1676620020691146024_WebcastRoomRankMessage-1676619972726895075_AudienceGiftSyncData'
                  r'-1676619980834317696_HighlightContainerSyncData-2&cursor=t-1676620021641_r-1_d-1_u-1_h-1&host'
                  r'=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&endpoint=live_pc&support_wrds'
                  r'=1&im_path=/webcast/im/fetch/&user_unique_id=%s&device_platform=web&cookie_enabled=true'
                  r'&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name'
                  r'=Mozilla&browser_version=5.0%20('
                  r'Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,'
                  r'%20like%20Gecko)%20Chrome/110.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai'
                  r'&identity=audience&room_id=%s&heartbeatDuration=0&signature=00000000')

        ws_url = ws_url.replace("%s", self.room_info.get('room_id'))
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
                # case "WebcastLikeMessage":
                #     self._parse_like_msg(msg.payload)
                # case "WebcastMemberMessage":
                #     self._parse_member_msg(msg.payload)
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
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload_pack.sendTime/1000))
        user_name = payload_pack.user.nickName
        gift_name = payload_pack.gift.name
        gift_cnt = payload_pack.comboCount
        print(f"{formatted_time} [礼物] {user_name}: {gift_name} * {gift_cnt}")

    @staticmethod
    def _parse_like_msg(payload):
        payload_pack = dy_pb2.LikeMessage()
        payload_pack.ParseFromString(payload)
        user_name = payload_pack.user.nickName
        like_cnt = payload_pack.count
        print(f"[点赞] {user_name}: 点赞 * {like_cnt}")

    @staticmethod
    def _parse_member_msg(payload):
        payload_pack = dy_pb2.MemberMessage()
        payload_pack.ParseFromString(payload)
        user_name = payload_pack.user.nickName
        print(f"[入场] {user_name} 进入直播间")

