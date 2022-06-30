# -*- coding: utf-8 -*-
"""
主程式檔
"""
from root.app import app, router
from root.view import view
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# LINE Bot
app.include_router(router) 
app.include_router(view)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["DNT","X-Mx-ReqToken","Keep-Alive","User-Agent","X-Requested-With","If-Modified-Since","Cache-Control","Content-Type","Authorization"],
)