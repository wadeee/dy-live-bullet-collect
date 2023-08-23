import os

import yaml

_env = os.environ.get('DY_LIVE_ENV', 'dev')  # 默认为 'dev'
print(f"当前环境为：{_env}")
with open(f"yml/config_{_env}.yml", 'r') as stream:
    content = yaml.safe_load(stream)
