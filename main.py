import logging

import douyin

if __name__ == '__main__':
    url = r'https://live.douyin.com/484785361988'
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    room_info = douyin.get_room_info(url)
    if room_info is not None:
        douyin.connect_web_socket(room_info)
