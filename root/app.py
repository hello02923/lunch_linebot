# -*- coding: utf-8 -*-
"""
Define the url entries for the whole webapp.
"""
from fastapi import (
    APIRouter, FastAPI, HTTPException, Request
)
from linebot.models import (
    MessageEvent, PostbackEvent, 
    FollowEvent, UnfollowEvent, AccountLinkEvent
)
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import bot.config as config
from bot.agent import Agent
from bot.utils.user import unfollow
from bot.const import apiurl

## swagger設定
app = FastAPI()
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
lunch_handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
line_agent = Agent()
## LOG 設定
router = APIRouter()


@router.post(f"/{apiurl}/callback")
async def callback(request: Request) -> str:

    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        lunch_handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter")
    return "OK"

    
@lunch_handler.add(FollowEvent)
def handle_follow(event) -> None:
    """Event - User follow LINE Bot

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#follow-event
    """
    line_agent.welcome_user(event=event)

@lunch_handler.add(UnfollowEvent)
def handle_unfollow(event) -> None:
    """Event - User follow LINE Bot

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#follow-event
    """
    unfollow(event.source.user_id)

@lunch_handler.add(AccountLinkEvent)
def handle_accountlink(event):
    """
    line bot account link callback
    """
    if event.link.result == 'ok':
        line_agent.link_account(event)
    else:
        print('at handle_accountlink error')
        print(event.link.result)

@lunch_handler.add(MessageEvent)
def handle_message(event) -> None:
    """Event - User sent message

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#message-event
    """
    if (event.message.type == "text"):
        content = event.message.text
        line_agent.parse_msg(event, content)

@lunch_handler.add(PostbackEvent)
def handle_postback(event) -> None:
    """
    line bot postback callback
    """
    content = event.postback.data
    line_agent.parse_msg(event, content)
