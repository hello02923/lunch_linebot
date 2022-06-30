#%%
# -*- coding: utf-8 -*-
"""
平日提醒訂購午餐
"""

from datetime import datetime
from bot.agent import Agent
# 推送訊息
number = datetime.today().isoweekday()
if number <6:
    line_agent = Agent()
    line_agent.push_reminder()


# %%
