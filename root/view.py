# -*- coding: utf-8 -*-
"""
明細頁
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from bot.utils.user import get_alluserinfo
from bot.const import apiurl
view = APIRouter()

## 路徑問題
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

#取得訂餐明細
@view.get(f"/{apiurl}/userinfo", response_class=JSONResponse)
async def userinfo(request: Request):
    data = get_alluserinfo()
    print(data)
    return JSONResponse(data)

#跳轉至明細頁
@view.get(f"/{apiurl}/", response_class=HTMLResponse)
async def userpage(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})
