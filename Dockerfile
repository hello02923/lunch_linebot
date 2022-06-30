FROM python:3.8.2

RUN mkdir lunch_linebot
WORKDIR lunch_linebot

COPY . ./

RUN apt-get update -y && apt-get install cron -y \
    && apt-get install vim -y
# 改成台北時區
RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
    
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 
# 下載套件
RUN pip install -r requirements.txt
# 設權限
RUN chmod -cR 700 *
# 設定crontab
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob && \
    crontab /etc/cron.d/cronjob

# 設定執行script
ADD start.sh /usr/local/bin/start.sh

RUN chmod 777 /usr/local/bin/start.sh

CMD /usr/local/bin/start.sh

# CMD uvicorn main:app --reload --port 5006 

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5006", "&&", "cron"]