from typing import Optional, Dict, Any
from telethon.tl.types import PeerChat, Channel
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaDice
from core.db_handler import db

def print_text(event) -> Dict[str, Any]:
    """
    打印消息详细信息并返回结构化数据
    
    参数:
        event: Telegram事件对象
        
    返回:
        包含消息信息的字典
    """
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
    
    try:
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
            if hasattr(message, 'media') and message.media:
                media_type = type(message.media).__name__
                print(f"📎 媒体类型: {media_type}")
                
                if isinstance(message.media, MessageMediaPhoto):
                    media_text = '[图片消息]'
                elif isinstance(message.media, MessageMediaDocument):
                    if hasattr(message.media.document, 'mime_type') and message.media.document.mime_type.startswith('video'):
                        media_text = '[视频消息]'
                    else:
                        media_text = '[文件消息]'
                elif isinstance(message.media, MessageMediaDice):
                    media_text = '[表情消息]'
                else:
                    media_text = f"[{media_type} 消息]"
                
                print(f"💬 消息内容👇👇👇👇👇👇👇👇👇\n {media_text}")
                data['message'] = media_text
            else:
                # 检查是否有文本内容
                text = getattr(message, 'text', None) or getattr(message, 'raw_text', None) or getattr(message, 'message', None)
                if text:
                    print(f"💬 消息内容👇👇👇👇👇👇👇👇👇\n {text}")
                    data['message'] = text
                else:
                    print(f"💬 消息内容👇👇👇👇👇👇👇👇👇\n [空消息]")
                    data['message'] = '[空消息]'
        
        print("\n")
        
        # 保存数据到数据库
        db.save_message(data)
        
        return data
        
    except Exception as e:
        print(f"处理消息时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise
