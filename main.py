import logging

import config
import douyin

if __name__ == '__main__':
    url = config.content['url']
    logging.basicConfig(level=config.content['log']['level'], format=config.content['log']['format'])
    room_info = douyin.get_room_info(url)
    if room_info is not None:
        douyin.connect_web_socket(room_info)
