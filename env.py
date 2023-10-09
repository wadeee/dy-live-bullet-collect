import os

from dotenv import load_dotenv

load_dotenv()

# have default
DY_LOG_LEVEL = None

# have default but need custom

# have no default


def init():
    global DY_LOG_LEVEL
    DY_LOG_LEVEL = os.environ.get("DY_LOG_LEVEL", "10")
