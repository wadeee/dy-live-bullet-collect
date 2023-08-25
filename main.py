import logging

import config
from douyin import Douyin

if __name__ == '__main__':
    url = config.content['url']
    logging.basicConfig(level=config.content['log']['level'], format=config.content['log']['format'])
    dy = Douyin(url)
    dy.connect_web_socket()
