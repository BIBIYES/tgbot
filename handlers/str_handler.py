"""字符串处理模块

该模块负责处理消息文本，根据配置的模式匹配并转发消息到指定机器人
"""

import re
import logging
from typing import Optional, List, Tuple
from telethon import TelegramClient
from core.config_manager import config_manager

# 配置日志
logger = logging.getLogger(__name__)

class TelegramSender:
    """Telegram 客户端单例类
    
    Attributes:
        _instance (Optional[TelegramClient]): 保存Telegram客户端实例
    """
    
    _instance: Optional[TelegramClient] = None
    
    @classmethod
    def set_client(cls, client: TelegramClient) -> None:
        """设置Telegram客户端实例
        
        Args:
            client: Telegram客户端实例
        """
        cls._instance = client
        logger.info("Telegram客户端已设置")
    
    @classmethod
    def get_client(cls) -> Optional[TelegramClient]:
        """获取Telegram客户端实例
        
        Returns:
            已设置的Telegram客户端实例，如果未设置则返回None
        """
        return cls._instance

def load_patterns_from_config() -> List[Tuple[re.Pattern, str]]:
    """从配置加载消息模式
    
    Returns:
        包含模式-机器人对列表
        
    Raises:
        ValueError: 当配置无效时抛出
    """
    try:
        patterns = []
        pattern_config = config_manager.patterns
        if not pattern_config:
            raise ValueError("未找到消息模式配置")
            
        for item in pattern_config:
            if not isinstance(item, dict) or 'pattern' not in item or 'bot' not in item:
                raise ValueError("无效的模式配置格式")
                
            pattern = re.compile(item['pattern'])
            bot = item['bot']
            patterns.append((pattern, bot))
            
        logger.info(f"成功加载 {len(patterns)} 个消息模式")
        return patterns
    except Exception as e:
        logger.error(f"加载消息模式失败: {str(e)}")
        raise ValueError("加载消息模式失败") from e

def str_handler(text: str) -> None:
    """处理消息文本
    
    Args:
        text: 要处理的文本内容
        
    Raises:
        RuntimeError: 当处理过程中发生错误时抛出
    """
    try:
        if not text:
            logger.warning("收到空消息文本")
            return
            
        logger.info(f"开始处理消息: {text[:50]}...")
        patterns = load_patterns_from_config()
        
        for pattern, bot in patterns:
            matches = pattern.findall(text)
            if matches:
                logger.info(f"找到 {len(matches)} 个匹配项")
                for match in matches:
                    send_to_someone(match, bot)
    except Exception as e:
        logger.error(f"处理消息时出错: {str(e)}")
        raise RuntimeError("消息处理失败") from e

def send_to_someone(text: str, bot: str) -> None:
    """发送消息到指定机器人
    
    Args:
        text: 要发送的消息内容
        bot: 目标机器人用户名
        
    Raises:
        ConnectionError: 当客户端未连接时抛出
        RuntimeError: 当发送消息失败时抛出
    """
    try:
        client = TelegramSender.get_client()
        if not client or not client.is_connected():
            raise ConnectionError("Telegram客户端未初始化或未连接")
            
        logger.info(f"正在发送消息到 {bot}: {text[:50]}...")
        client.loop.create_task(client.send_message(bot, text))
        logger.info("消息发送任务已创建")
    except ConnectionError as e:
        logger.error(f"连接错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise RuntimeError("消息发送失败") from e
