import logging

import config
import env
from douyin import Douyin

env.init()

if __name__ == '__main__':
    url = config.content['url']
    logging.basicConfig(level=int(env.DY_LOG_LEVEL), format=config.content['log']['format'])


    def on_message(message):
        print(message)


    dy = Douyin(url, on_message)
    dy.connect_web_socket()
