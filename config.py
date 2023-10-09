import os

import yaml

import static

with open(static.resource_path(f"static/config.yml"), 'r') as stream:
    content = yaml.safe_load(stream)
