#%%
from datetime import datetime
from pymongo import MongoClient
import pandas as pd

client = MongoClient('172.21.80.253:27017', username='cathy', password='cathy')
db = client['Lunch']
data_Menu = list(db.Menu.find({},{'_id':0}))
data_UserOrder = list(db.UserOrder.find({},{'_id':0}))
data_User = list(db.User.find({},{'_id':0}))
# %%
client_u = MongoClient('172.21.80.251:27017', username='cathy', password='cathy')
db_u = client_u['Lunch']
db_u.Menu.insert_many(data_Menu)
db_u.UserOrder.insert_many(data_UserOrder)
db_u.User.insert_many(data_User)
# %%
