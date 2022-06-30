# -*- coding: utf-8 -*-
"""
訊息管理
"""
import sys
import bot.config as config
from datetime import datetime
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, FlexSendMessage, ImageSendMessage,
    TextComponent, SeparatorComponent, BoxComponent,
    BubbleContainer, BoxComponent, ButtonComponent,
    PostbackAction, QuickReplyButton, QuickReply,
    URIAction, CarouselContainer
)

from .utils.user import (
    get_res, get_menu, get_records, get_userinfo, get_user,
    map_user, check_user, get_alluser, check_ordertime
)
from .const import (
    tip_msg, welcome_msg, delete_msg,unblind_msg, unblindtip_msg, help_msg,
    imgurl, background_color, yellow_color, white_color, default_msg
)

from bot.line_agent import LineAgent

sys.path.append(".")

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)

class Agent(LineAgent):

    def __init__(self):
        super().__init__('Lunch')

    # 新增用戶收集資料
    def welcome_user(self, event, action=None):
        line_id = event.source.user_id

        portfolio = line_bot_api.get_profile(line_id)
        msg_group = list()

        # 尚未綁定英文名稱
        if action == 'unblind':
            title = unblind_msg
            tip = unblindtip_msg
        else:
            title = welcome_msg%portfolio.display_name
            tip = tip_msg

        ## 請他先綁定英文名稱
        welcome_items = TextComponent(text=title, size='md', wrap=True)
        tips_items = TextComponent(text=tip, size='sm', wrap=True)
        bubble = BubbleContainer(
            direction='ltr',
            size='kilo',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    welcome_items,
                    tips_items
                ]
            )
        )

        msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
        line_bot_api.reply_message(event.reply_token, msg_group)

    # 顯示餐廳
    def show_store(self):
        body_items = list()
        data = get_res()
        for store in data:
            res_items = ButtonComponent(
                style='primary',height='sm', color=background_color, warp=False,
                action=PostbackAction(label=f'{store}', data=f'/res&restuarant={store}')
            )
            bubble = BubbleContainer(
                direction='ltr',
                size='micro',
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        res_items
                    ]
                )
            )
            body_items.append(bubble)
        bubble = CarouselContainer(body_items)
        return bubble
    

    # 綁定uid & 英文名稱
    def blind_user(self, event, content):
        line_id = event.source.user_id
        msg_group = list()
        # 判斷是否有用戶
        if check_user(line_id=line_id):
            # 如果有該用戶 就無法個別回覆
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='😰無法個別回覆～'))
        else:
            # 還沒有該用戶
            # 比對名稱
            map_user(username=content, line_id=line_id)
            msg_group.append(TextSendMessage(text='綁定完成😄如有問題請找Cathy#575'))
            
            bubble = self.show_store()
            msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
            
            line_bot_api.reply_message(event.reply_token, msg_group)

    # 顯示餐廳
    def reply_store(self, event, action=None):
        msg_group = list()
        line_id = event.source.user_id
        
       # 判斷用戶是否已經綁定
        if check_user(line_id=line_id):
            # 刪除資料
            if action == 'delete':    
                get_records(
                    line_id=line_id, 
                    action='delete',
                )
                ## 取消完成
                check_items = TextComponent(text=delete_msg, size='md', wrap=True)
                bubble = BubbleContainer(
                    direction='ltr',
                    size='kilo',
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            check_items
                        ]
                    )
                )

                msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
            
            # 抓取該用戶今日訂餐項目
            username = get_user(line_id=event.source.user_id)
            data = get_userinfo(username)
            # 如果已經不能點餐 超過兩份 跳查看明細
            if len(data) >=2:
                question_items = TextComponent(text='今日已選擇兩項餐點😊', size='lg', wrap=True, margin='lg')
                check_items = ButtonComponent(
                    style='primary', height='sm', color=background_color, margin='md',
                    action=PostbackAction(
                        label='查看明細',
                        data=f'查看明細'
                    ),
                )

                bubble = BubbleContainer(
                    direction='ltr',
                    size='giga',
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            question_items,
                            check_items
                        ]
                    )
                )

                msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
                
            else:
                bubble = self.show_store()
                msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
            
            line_bot_api.reply_message(event.reply_token, msg_group)
        # 用戶還未存在 先請他輸入英文名稱
        else:
            self.welcome_user(event, action='unblind')
    
    # 顯示餐廳的菜單
    def reply_storeorder(self, event, content):
        msg_group = list()
        body_items = list()

        restuarant = content[1].split('=')[1]
        # 顯示蔡老師的菜單
        if restuarant == '蔡老師':
            img_item = ImageSendMessage(original_content_url=imgurl, preview_image_url=imgurl)
            msg_group.append(img_item)

        data = get_menu(restaurant=restuarant)

        num=0
        for order in data:
            num+=1
            color = yellow_color if (num % 2) == 0 else white_color

            order = order['order']
            id_item = BoxComponent(
                layout='baseline', margin='md',
                spacing='lg', background_color=color,
                contents=[
                    TextComponent(
                        text=f'{order}', size='lg',align='center', 
                        action=PostbackAction(label=f'{order}', data=f'/ord&restuarant={restuarant}&order={order}')
                    )
                ]
            )
            
            ## 淺線間隔
            space_items = SeparatorComponent(margin="md", color=background_color)
        
            body_items.append(id_item)
            body_items.append(space_items)

        bubble = BubbleContainer(
            direction='ltr',
            size='giga',
            body=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=body_items
            )
        )
        
        msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
        line_bot_api.reply_message(event.reply_token, msg_group)
    
    # 確定是否點餐
    def reply_checkorder(self, event, content):
        """
        content: ['/ord', 'restuarant='紫琳', 'order='牛肉細粉']
        """
        msg_group = list()

        restuarant = content[1].split('=')[1]
        order = content[2].split('=')[1]

        question_items = TextComponent(text=f'確定要訂購{order}?', size='lg', wrap=True, margin='md')
        
        yes_items = ButtonComponent(
            style='primary', height='sm', color=background_color, margin='md',
            action=PostbackAction(
                label='確定',
                data=f'/check&restuarant={restuarant}&order={order}'
            ),
        )
        no_items = ButtonComponent(
            style='primary', height='sm', color=background_color, margin='md',
            action=PostbackAction(
                label='返回',
                data=f'/res&restuarant={restuarant}'
            ),
        )

        bubble = BubbleContainer(
            direction='ltr',
            size='giga',
            body=BoxComponent(
                layout='vertical',
                spacing='none',
                contents=[
                    question_items,
                    yes_items,
                    no_items
                ]
            )
        )

        msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
        line_bot_api.reply_message(event.reply_token, msg_group)
    
    # 是否要新增其他餐點
    def reply_addmoreorder(self, event, content):
        """
        content: ['/check', 'restuarant='紫琳', 'order='牛肉細粉']
        """
        msg_group = list()
        
        username = get_user(line_id=event.source.user_id)
        # 判斷在訂餐時間
        if check_ordertime():
          ## 訂餐完成
          check_items = TextComponent(text='訂餐完成!請至明細查看訂餐紀錄', size='md', wrap=True)
          bubble = BubbleContainer(
              direction='ltr',
              size='kilo',
              header=BoxComponent(
                  layout='vertical',
                  contents=[
                      check_items
                  ]
              )
          )

          msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))

          try:
              # 抓取該用戶今日訂餐項目
              data = get_userinfo(username)
              # 判斷是否能新增 每日上限為2
              if len(data) <2:
                  restaurant = content[1].split('=')[1]
                  order = content[2].split('=')[1]
                  # 新噌餐點
                  get_records(
                      line_id=event.source.user_id, 
                      action='create', 
                      restaurant=restaurant, 
                      order=order
                  )
              else:
                  question_items = TextComponent(text='今日已選擇兩項餐點😊', size='lg', wrap=True, margin='lg')
                  check_items = ButtonComponent(
                      style='primary', height='sm', color=background_color, margin='md',
                      action=PostbackAction(
                          label='查看明細',
                          data=f'查看明細'
                      ),
                  )

                  bubble = BubbleContainer(
                      direction='ltr',
                      size='giga',
                      body=BoxComponent(
                          layout='vertical',
                          contents=[
                              question_items,
                              check_items
                          ]
                      )
                  )

                  msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
                  line_bot_api.reply_message(event.reply_token, msg_group)
                  return 

          except:
              line_bot_api.reply_message(event.reply_token, TextSendMessage(text='有東西出錯囉😅 請稍候'))
              return 

          # 抓取該用戶今日訂餐項目
          data = get_userinfo(username)
          # 判斷是否能新增 每日上限為2
          if len(data) <2:
              question_items = TextComponent(text='是否有要新增其他餐點?☺️', size='lg', wrap=True, margin='md')
              tip_items = TextComponent(text='👉🏻提醒:每人上限為兩種餐點', size='lg', wrap=True, margin='md')
              
              yes_items = ButtonComponent(
                  style='primary', height='sm', color=background_color, margin='md',
                  action=PostbackAction(
                      label='是🥳',
                      data=f'點餐'
                  ),
              )
              no_items = ButtonComponent(
                  style='primary', height='sm', color=background_color, margin='md',
                  action=PostbackAction(
                      label='否(查看明細)',
                      data=f'查看明細'
                  ),
              )
              body_items = [
                  question_items,
                  tip_items,
                  yes_items,
                  no_items
              ]

          else:
              question_items = TextComponent(text='今日已選擇兩項餐點😊', size='lg', wrap=True, margin='lg')
              check_items = ButtonComponent(
                  style='primary', height='sm', color=background_color,
                  action=PostbackAction(
                      label='查看明細',
                      data=f'查看明細'
                  ),
              )
              body_items = [
                  question_items,
                  check_items
              ]

          bubble = BubbleContainer(
              direction='ltr',
              size='giga',
              body=BoxComponent(
                  layout='vertical',
                  contents=body_items
              )
          )
            
          msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
          line_bot_api.reply_message(event.reply_token, msg_group)
        # 判斷超過訂餐時間
        else:
          line_bot_api.reply_message(event.reply_token, TextSendMessage(text='超過訂餐時間，無法訂餐！'))
           
        
        

    # 訂單明細
    def reply_completeorder(self, event):
        
        msg_group = list()
        body_items = list()

        today = datetime.today().strftime('%Y-%m-%d')
        line_id = event.source.user_id
        
        
        # 判斷是否有用戶
        if check_user(line_id=line_id):
            username = get_user(line_id=event.source.user_id)
            
            header_item = TextComponent(text=f'{today} {username}的點餐明細', size='md', weight='bold')
            
            # 取得用戶餐點紀錄
            data = get_userinfo(username=username)
            for item in data:
                body_items.append(
                    TextComponent(text=item['order'], size='md', wrap=True, weight='bold', margin='md')
                )
            # 最多每人點兩項
            if len(data) < 2:

                add_item = ButtonComponent(
                        style='primary', height='sm',color=background_color, margin='md',
                        action=PostbackAction(label='新增餐點', data='點餐'),
                )
                body_items.append(add_item)

            # len(data) == 1 or  == 2 時可以取消餐點
            if len(data) == 1 or len(data) == 2: 
                
                delete_item = ButtonComponent(
                        style='primary', height='sm',color=background_color, margin='md',
                        action=PostbackAction(label='取消餐點', data='/delete'),
                )
                body_items.append(delete_item)

            bubble = BubbleContainer(
                direction='ltr',
                size='giga',
                header=BoxComponent(
                    layout='vertical',
                    spacing='none',
                    background_color=yellow_color,
                    contents=[
                        header_item
                    ]
                ),
                body=BoxComponent(
                    layout='vertical',
                    spacing='none',
                    contents=body_items
                )
            )

            msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
            line_bot_api.reply_message(event.reply_token, msg_group)

        # 用戶還未存在 先請他輸入英文名稱
        else:
            self.welcome_user(event, action='unblind')

    # 再次確認是否刪除餐點
    def reply_checkdelete(self, event):
        msg_group = list()

        question_items = TextComponent(text=f'確定要取消餐點?', size='lg', wrap=True, margin='md')
        
        yes_items = ButtonComponent(
            style='primary', height='sm', color=background_color, margin='md',
            action=PostbackAction(
                label='確定',
                data=f'/取消餐點'
            ),
        )
        no_items = ButtonComponent(
            style='primary', height='sm', color=background_color, margin='md',
            action=PostbackAction(
                label='返回',
                data=f'查看明細'
            ),
        )

        bubble = BubbleContainer(
            direction='ltr',
            size='giga',
            body=BoxComponent(
                layout='vertical',
                spacing='none',
                contents=[
                    question_items,
                    yes_items,
                    no_items
                ]
            )
        )

        msg_group.append(FlexSendMessage(alt_text=default_msg, contents=bubble))
        line_bot_api.reply_message(event.reply_token, msg_group)

    # 輔助工具
    def reply_help(self, event):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_msg))


    # 推送提醒要訂餐
    def push_reminder(self):
        users_list  = get_alluser()
        bubble = self.show_store()
        msg_group = list()
        msg_group.append(FlexSendMessage(alt_text='提醒👏要記得訂午餐', contents=bubble))
        # ['Uadaeafc96db05776f83f1bf861ecdc10']
        for user_id in users_list:
            line_bot_api.push_message(user_id, msg_group)

    # 回覆控制區
    def parse_msg(self, event, content) -> None:
        """ response correct behavior based on receivec message
        :param event: the received message event
        """


        texts = content.split('&')
        text = texts[0]

        
        if text == '/help':
            self.reply_help(event)

        elif text == '點餐' or text == '1':
            self.reply_store(event)

        elif text == '/res':
            self.reply_storeorder(event, texts)
        
        elif text == '/ord':
            self.reply_checkorder(event, texts)

        elif text == '/check':
            self.reply_addmoreorder(event, texts)
        
        elif text == '查看明細' or text == '2':
            self.reply_completeorder(event)
        
        elif text == '/delete':
            self.reply_checkdelete(event)

        elif text == '/取消餐點':
            self.reply_store(event, action='delete')
            
            
        else:
            self.blind_user(event, text)
            
            
        
            