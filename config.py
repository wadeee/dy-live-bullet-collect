import os

import yaml

import static

_env = os.environ.get('DY_LIVE_ENV', 'dev')  # 默认为 'dev'
print(f"当前环境为：{_env}")
with open(static.resource_path(f"static/config_{_env}.yml"), 'r') as stream:
    content = yaml.safe_load(stream)
