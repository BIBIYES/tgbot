from telethon.tl.types import PeerUser, PeerChat, PeerChannel, MessageEntityMention, Channel
from db_handler import db

def message_handler(events):
    # 过滤掉自己的消息
    if events.out:
        return
    # 消息筛选
    if events.message and not events.media:
        # 文本消息
        print_text(events)
    elif hasattr(events, 'media'):
        if isinstance(events.media, events.MessageMediaPhoto):
            # 图片消息
            print(f"图片消息")
        elif isinstance(events.media, events.MessageMediaDocument):
            # 文件或媒体消息
            print(f"媒体消息")
        elif isinstance(events.media, events.MessageMediaDice):
            # 表情或骰子消息
            print(f"表情消息")
        else:
            # 其他类型
            print(f"其他消息: {events.message}")

def print_text(event):
    """打印消息详细信息"""
    try:
        # 准备要保存的数据
        data = {
            'username': '否',
            'first_name': '否',
            'last_name': '否',
            'user_id': None,
            'chat_type': '否',
            'chat_title': '否',
            'chat_id': None,
            'message': '否',
            'date': None,
            'is_bot': False
        }
        
        # 安全地获取发送者信息
        sender = getattr(event, 'sender', None)
        message = getattr(event, 'message', '')
        chat = getattr(event, 'chat', None)
        
        print(f"\n📥 新消息!================================================")
        
        # 处理发送者信息
        if sender:
            username = getattr(sender, 'username', None)
            if username:
                print(f"🧔用户名: @{username}")
                data['username'] = username
            
            first_name = getattr(sender, 'first_name', None)
            if first_name:
                print(f"👤 名称: {first_name}")
                data['first_name'] = first_name
            
            last_name = getattr(sender, 'last_name', None)
            if last_name:
                print(f"👥 姓氏: {last_name}")
                data['last_name'] = last_name
            
            user_id = getattr(sender, 'id', None)
            if user_id:
                print(f"🆔 用户ID: {user_id}")
                data['user_id'] = user_id
            
            bot = getattr(sender, 'bot', False)
            if bot:
                print(f"🤖 是否Bot: 是")
                data['is_bot'] = True
        
        # 处理消息时间和Chat ID
        if message:
            date = getattr(message, 'date', '')
            if date:
                print(f"⏰ 发送时间: {date}")
                data['date'] = date
            
            chat_id = getattr(message, 'chat_id', None)
            if chat_id:
                print(f"🏠 Chat ID: {chat_id}")
                data['chat_id'] = chat_id
        
        # 处理聊天信息
        if chat:
            if isinstance(chat, Channel):
                if chat.broadcast:
                    print(f"📢 这是频道: {chat.title}")
                    data['chat_type'] = 'channel'
                else:
                    print(f"👥 这是超级群组: {chat.title}")
                    data['chat_type'] = 'supergroup'
                data['chat_title'] = chat.title
            elif isinstance(chat, PeerChat):
                print("👥 这是一个群组。")
                data['chat_type'] = 'group'
            else:
                print("🏷️ 这是私人聊天。")
                data['chat_type'] = 'private'

        # 处理消息内容
        if message:
            text = getattr(message, 'text', '')
            if text:
                print(f"💬 消息内容👇👇👇👇👇👇👇👇👇\n {text}")
                data['message'] = text
        print("\n")
        
        # 保存数据到数据库
        db.save_message(data)
        
    except Exception as e:
        print(f"Error: {e}")