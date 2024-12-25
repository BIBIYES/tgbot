import re
import json
from typing import Optional, List, Tuple
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

def load_patterns_from_config() -> List[Tuple[re.Pattern, str]]:
    patterns = []
    with open('patterns.json', 'r') as f:
        pattern_config = json.load(f)
        for item in pattern_config:
            pattern = re.compile(item['pattern'])
            bot = item['bot']
            patterns.append((pattern, bot))
    return patterns

def str_handelr(text: str):
    patterns = load_patterns_from_config()
    
    for pattern, bot in patterns:
        matches = pattern.findall(text)
        for match in matches:
            send_to_someone(match, bot)

def send_to_someone(text: str, bot: str):
    client = TelegramSender.get_client()
    if client and client.is_connected():
        print(f"发送消息到 {bot}: {text}")
        # 使用异步方式发送消息
        client.loop.create_task(client.send_message(bot, text))
    else:
        print("错误：TelegramClient 未初始化或未连接")
