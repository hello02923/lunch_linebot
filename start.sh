#!/bin/bash
cron

uvicorn main:app --reload --port 5006 