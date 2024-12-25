import re
import json
from typing import Optional
from telethon import TelegramClient

# 从配置文件中读取API_ID和API_HASH
with open('config.json', 'r') as f:
    config = json.load(f)
API_ID = config['API_ID']
API_HASH = config['API_HASH']

class TelegramSender:
    _instance: Optional[TelegramClient] = None
    
    @classmethod
    def set_client(cls, client: TelegramClient):
        cls._instance = client
    
    @classmethod
    def get_client(cls) -> Optional[TelegramClient]:
        return cls._instance

def str_handelr(text: str):
    pattern = re.compile(r'showfilesbot.{24}')
    matches = pattern.findall(text)
    for match in matches:
        send_to_someone(match)

def send_to_someone(text: str):
    client = TelegramSender.get_client()
    if client and client.is_connected():
        print(f"发送消息: {text}")
        # 使用异步方式发送消息
        client.loop.create_task(client.send_message('@ShowFilesBot', text))
    else:
        print("错误：TelegramClient 未初始化或未连接")
