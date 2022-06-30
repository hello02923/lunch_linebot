# -*- coding: utf-8 -*-

"""
line agent behavior
logging 設定

"""
# import logging
from linebot import LineBotApi
from bot.config import LINE_CHANNEL_ACCESS_TOKEN


class LineAgent():
    """LineAgentApi provides interface for LINE agent bot API."""

    def __init__(self, name):
        """__init__ method.
        """
        self.name = name
        self.logging = True
        self.line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

        if self.logging:
            print('Start')

