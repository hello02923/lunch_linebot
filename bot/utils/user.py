# -*- coding: utf-8 -*-
"""
用戶及餐點
"""
#%%
import os
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
# from ..config import mongo_db_url
mongo_db_url = '{mongodb}:27017'
client = MongoClient(mongo_db_url, username='cathy', password='cathy')
db = client['Lunch']
#%%
# 更新項目
# db.Menu.update_many({'menu':'紅豆紫米粥'}, {"$set": {"status": 0}}, upsert=False, array_filters=None)
# data = list(db.Menu.find({'menu':{"$regex" : "1~15"}}, {'menu':1, '_id':0}))
# d = list(map(lambda x : x['menu'], data))
#%%
# d = ['義式烤雞腿飯']
# db.Menu.update_many({'menu':{'$in':d}}, {"$set": {"status": 3}}, upsert=False, array_filters=None)
#%％
#判斷訂餐時間是否有效
def check_ordertime():
  now = datetime.now()
  ret = False if (now.hour, now.minute) >= (9, 45) else True
  return ret
#%%
# 封鎖用戶 刪除資料
def unfollow(line_id):
    today = datetime.today()
    today =datetime(
        today.year,
        today.month,
        today.day,0,0
    )
    
    user = get_user(line_id=line_id)
    # 刪除用戶資料
    db.User.delete_one({'line_id':line_id})
    # 刪除用戶今日訂餐資料
    db.UserOrder.delete_many({'username':user, 'date':today})
    return 

#判斷用戶是否存在
def check_user(line_id):
    ret = False
    if db.User.find_one({'line_id':line_id}):
        ret = True
    return ret

# 比對用戶名稱
def map_user(username, line_id):
    db.User.insert_one({
        'username':username,
        'line_id':line_id,
        'created_at':datetime.now()
    })
    return 

# 用戶名稱
def get_user(line_id):
    user = db.User.find_one({'line_id':line_id},{'_id':0, 'username':1})
    return user['username']

# 取得餐廳
def get_res():
    data = list(db.Menu.distinct('restaurant'))
    return (sorted(data, reverse = True))

# 取得該餐廳之菜單
def get_menu(restaurant):
    # the chip 菜單變換
    if datetime.today().day <= 15:
        status = [1, 2]
    else:
        status = [1, 3]

    df = pd.DataFrame(db.Menu.find({'restaurant':restaurant, 'status':{'$in':status}},{'_id':0}).sort('price', 1))
    df['order'] = df['menu'] +' $'+ df['price'].astype(str)
    
    return df.sort_values(by=['order']).to_dict('records')

# 紀錄用戶新增餐點或是刪除
def get_records(line_id, action, restaurant=None, order=None):
    today = datetime.today()
    today =datetime(
        today.year,
        today.month,
        today.day,0,0
    )

    user = get_user(line_id=line_id)
    try:
        if action == 'create':
            db.UserOrder.insert_one({
                'date':today,
                'username':user,
                'restaurant':restaurant,
                'order':order
            })
        elif action == 'delete':
            db.UserOrder.delete_many({
                'date':today,
                'username':user
            })
        ret = True
    except:
        ret = False
    return ret

# 取得該用戶今日訂餐明細
def get_userinfo(username):
    today = datetime.today()
    today =datetime(
        today.year,
        today.month,
        today.day,0,0
    )
    data = list(db.UserOrder.find({'username':username, 'date':today}, {'_id':0, 'username':1, 'order':1}))
    return data

# 取得當日所有點餐紀錄
def get_alluserinfo():
    today = datetime.today()
    today =datetime(
        today.year,
        today.month,
        today.day,0,0
    )
    data = list(db.UserOrder.find({'date':today}, {'_id':0, 'date':0}))
    return data

# 獲取所有用戶line_id
def get_alluser():
    today = datetime.today()
    today =datetime(
        today.year,
        today.month,
        today.day,0,0
    )
    # 選取今日已訂餐之用戶
    has_users = list(db.UserOrder.find({'date':today},{'_id':0, 'username':1}))
    has_users = list(map(lambda x : x['username'], has_users))
    # 僅推送給 未訂餐用戶
    users = list(db.User.find({'username':{'$nin':has_users}}, {'_id':0, 'line_id':1}))
    return list(map(lambda x : x['line_id'], users))



