import gzip
import json
import logging
import re
import time
from datetime import datetime

import requests
import websocket
import pandas as pd
import config
import live_rank
from protobuf import dy_pb2


class Douyin:

    def __init__(self, url):
        self.ws_conn = None
        self.url = url
        self.chat_messages = pd.DataFrame(columns=['时间', '用户', '消息'])
        self.gift_messages = pd.DataFrame(columns=['时间', '用户', '礼物', '数量'])
        self.like_messages = pd.DataFrame(columns=['时间', '用户', '点赞次数'])
        self.member_messages = pd.DataFrame(columns=['时间', '用户'])
        self.file_name = 'Douyin_Chat_Messages.xlsx'
        self.message_count = 0  # 初始化消息计数器

    def start_douyin_stream(url):
        dy = Douyin(url)
        dy.connect_web_socket()

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
        re_pattern_room_id = r'\\"roomId\\":\\"(.*?)\\"'
        re_obj_room_id = re.compile(re_pattern_room_id)
        matches_room_id = re_obj_room_id.findall(res_origin_text)
        live_room_id = live_room_title = None
        for match_item in matches_room_id:
            if len(match_item) == 19:
                live_room_id = match_item
        re_pattern_title = r'"live-room-name">(.*?)</h1>'
        re_obj_title = re.compile(re_pattern_title)
        matches_title = re_obj_title.findall(res_origin_text)
        for match_item in matches_title:
            if len(match_item) > 0:
                live_room_title = match_item

        self.room_info = {
            'url': self.url,
            'ttwid': ttwid,
            'room_id': live_room_id,
            'room_title': live_room_title,
        } if live_room_id else None

    def connect_web_socket(self):
        self._get_room_info()
        self.parseLiveRoomUrl()
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

    def parseLiveRoomUrl(self):
        """
        解析直播的弹幕websocket地址
        :param url:直播地址
        :return:
        """
        h = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'cookie': '__ac_nonce=0638733a400869171be51',
        }
        res = requests.get(url=self.url, headers=h)
        global ttwid, roomStore, liveRoomId, liveRoomTitle, live_stream_url
        data = res.cookies.get_dict()
        ttwid = data['ttwid']
        res = res.text
        res_room = re.search(r'roomId\\":\\"(\d+)\\"', res)
        # 获取直播主播的uid和昵称等信息
        live_room_search = re.search(r'owner\\":(.*?),\\"room_auth', res)
        # 如果没有获取到live_room信息，很有可能是直播已经关闭了，待优化
        live_room_res = live_room_search.group(1).replace('\\"', '"')
        live_room_info = json.loads(live_room_res)
        print(f"主播账号信息: {live_room_info}")
        # 直播间id
        liveRoomId = res_room.group(1)
        # 获取m3u8直播流地址：m3u8直播比flv延迟2秒左右
        res_stream = re.search(r'hls_pull_url_map\\":(\{.*?})', res)
        res_stream_m3u8s = json.loads(res_stream.group(1).replace('\\"', '"'))
        # HD1和FULL_HD1随机获取，优先获取FULL_HD1
        res_m3u8_hd1 = res_stream_m3u8s.get("FULL_HD1", "").replace("http", "https")
        if not res_m3u8_hd1:
            res_m3u8_hd1 = res_m3u8_hd1.get("HD1", "").replace("http", "https")
        print(f"直播流m3u8链接地址是: {res_m3u8_hd1}")
        # 找到flv直播流地址:区分标清|高清|蓝光
        res_flv_search = re.search(r'flv\\":\\"(.*?)\\"', res)
        res_stream_flv = res_flv_search.group(1).replace('\\"', '"').replace("\\\\u0026", "&")
        if "https" not in res_stream_flv:
            res_stream_flv = res_stream_flv.replace("http", "https")
        print(f"直播流FLV地址是: {res_stream_flv}")
        # 开始获取直播间排行
        live_rank.interval_rank(liveRoomId)

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

    def _add_to_dataframe(self, new_row, sheet_name):
        if sheet_name == '礼物':
            self.gift_messages = self.gift_messages._append(new_row, ignore_index=True)
            if len(self.gift_messages) >= 100:
                self._save_to_excel(self.gift_messages, '礼物')
                self.gift_messages = self.gift_messages.iloc[0:0]  # 清空DataFrame
        elif sheet_name == '弹幕':
            self.chat_messages = self.chat_messages._append(new_row, ignore_index=True)
            if len(self.chat_messages) >= 100:
                self._save_to_excel(self.chat_messages, '弹幕')
                self.chat_messages = self.chat_messages.iloc[0:0]  # 清空DataFrame
        elif sheet_name == '点赞':
            self.like_messages = self.like_messages._append(new_row, ignore_index=True)
            if len(self.like_messages) >= 100:
                self._save_to_excel(self.like_messages, '点赞')
                self.like_messages = self.like_messages.iloc[0:0]  # 清空DataFrame
        elif sheet_name == '入场':
            self.member_messages = self.member_messages._append(new_row, ignore_index=True)
            if len(self.member_messages) >= 100:
                self._save_to_excel(self.member_messages, '入场')
                self.member_messages = self.member_messages.iloc[0:0]  # 清空DataFrame

    def _save_to_excel(self, dataframe, sheet_name):
        # 保存DataFrame到Excel的特定工作表
        try:
            with pd.ExcelWriter(self.file_name, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        except FileNotFoundError:
            dataframe.to_excel(self.file_name, sheet_name=sheet_name, index=False)

    @staticmethod
    def _on_error(ws, error):
        logging.error(error)

    @staticmethod
    def _on_close(ws, close_status_code, close_msg):
        logging.info("Websocket closed")

    @staticmethod
    def _on_open(ws):
        logging.info("Websocket opened")

    # @staticmethod
    def _parse_chat_msg(self, payload):
        self.message_count += 1
        payload_pack = dy_pb2.ChatMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload_pack.eventTime))
        user_name = payload_pack.user.nickName
        content = payload_pack.content

        # ...解析聊天消息的代码...
        new_row = {'时间': formatted_time, '用户': user_name, '消息': content}
        self._add_to_dataframe(new_row, '弹幕')  # 注意参数的更改

        print("self.message_count", self.message_count)
        print(f"{formatted_time} [弹幕] {user_name}: {content}")

    # @staticmethod
    def _parse_gift_msg(self, payload):
        payload_pack = dy_pb2.GiftMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName
        gift_name = payload_pack.gift.name
        gift_cnt = payload_pack.comboCount

        # ...解析礼物消息的代码...
        new_row = {'时间': formatted_time, '用户': user_name, '礼物': gift_name, '数量': gift_cnt}
        self._add_to_dataframe(new_row, '礼物')  # 注意参数的更改
        print(f"{formatted_time} [礼物] {user_name}: {gift_name} * {gift_cnt}")

    # @staticmethod
    def _parse_like_msg(self, payload):
        payload_pack = dy_pb2.LikeMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName
        like_cnt = payload_pack.count
        # ...解析点赞消息的代码...
        new_row = {'时间': formatted_time, '用户': user_name, '点赞次数': like_cnt}
        self._add_to_dataframe(new_row, '点赞')
        print(f"{formatted_time} [点赞] {user_name}: 点赞 * {like_cnt}")

    # @staticmethod
    def _parse_member_msg(self, payload):
        payload_pack = dy_pb2.MemberMessage()
        payload_pack.ParseFromString(payload)
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = payload_pack.user.nickName

        # ...解析会员消息的代码...
        new_row = {'时间': formatted_time, '用户': user_name}
        self._add_to_dataframe(new_row, '入场')
        print(f"{formatted_time} [入场] {user_name} 进入直播间")
