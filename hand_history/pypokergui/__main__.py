import os
import sys

# Resolve path configuration
root = os.path.join(os.path.dirname(__file__), "..")
src = os.path.join(root, "pypokergui")
sys.path.append(root)
sys.path.append(src)

import webbrowser

from pypokergui.server.poker import start_server
from pypokergui.config_builder import build_config


def serve_command(config: str = "poker_conf.yaml", port: int = 8000, speed: str = "moderate"):
    host = "localhost"
    webbrowser.open("http://%s:%s" % (host, port))
    start_server(config, port, speed)


def build_config_command(maxround: int = 10, stack: int = 100, small_blind: int = 5, ante: int = 0):
    build_config(maxround, stack, small_blind, ante)


if __name__ == '__main__':
    serve_command()


# (pokerAI) D:\ROBOTA\python\PyPokerEngine-master\pokerAI\Lib\site-packages\pypokergui>python __main__.py