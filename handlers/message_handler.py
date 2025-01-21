import re
import logging
import asyncio
from typing import Optional, List, Dict, Any
from telethon import TelegramClient
from telethon import events
from telethon.errors import ChatForwardsRestrictedError
from telethon.tl.custom import Message
from utils.message_tools import print_text
from core.config_manager import config_manager

logger = logging.getLogger(__name__)

class MessageHandler:
    """处理Telegram消息的类
    
    Attributes:
        client (TelegramClient): Telegram客户端实例
        target_channel (str): 目标频道用户名或ID
        patterns (List[Dict[str, Any]]): 消息匹配模式列表
    """

    def __init__(self, client: TelegramClient):
        """初始化消息处理器
        
        Args:
            client (TelegramClient): Telegram客户端实例
        """
        self.client = client
        self.target_channel = config_manager.target_channel
        self.patterns = [
            {
                "pattern": re.compile(p["pattern"]),
                "bot": p["bot"]
            }
            for p in config_manager.patterns
        ]

    async def handle_message(self, event: events.NewMessage.Event) -> None:
        """处理新消息事件
        
        Args:
            event (events.NewMessage.Event): 新消息事件对象
            
        Raises:
            Exception: 当消息处理失败时抛出
        """
        try:
            # 过滤自己的消息
            if event.message.out:
                return
                
            # 过滤配置的群组ID
            chat_id = event.message.chat_id
            if chat_id in config_manager.blocked_chat_ids:
                logger.info(f"跳过屏蔽群组消息: {chat_id}")
                return
                
            message_data = print_text(event)
            message_text = message_data.get('message', '')
            
            if self.target_channel:
                await self._forward_message_with_retry(event, self.target_channel)
            
            for pattern in self.patterns:
                if pattern["pattern"].search(message_text):
                    await self._forward_message_with_retry(event, pattern["bot"])
                    
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}", exc_info=True)
            raise

    async def _forward_message_with_retry(
        self, 
        event: events.NewMessage.Event, 
        target: str, 
        max_retries: int = 3
    ) -> None:
        """带重试机制的转发消息
        
        Args:
            event (events.NewMessage.Event): 新消息事件对象
            target (str): 目标频道用户名或ID
            max_retries (int): 最大重试次数，默认为3
            
        Raises:
            Exception: 当转发失败且达到最大重试次数时抛出
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                await self._forward_message(event, target)
                logger.info(f"消息已成功转发到: {target}")
                return
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"转发消息到 {target} 失败: {str(e)}", exc_info=True)
                    raise
                wait_time = min(2 ** retry_count, 10)
                logger.warning(f"转发失败，{wait_time}秒后重试...")
                await asyncio.sleep(wait_time)

    async def _forward_message(
        self, 
        event: events.NewMessage.Event, 
        target: str
    ) -> None:
        """直接转发消息
        
        Args:
            event (events.NewMessage.Event): 新消息事件对象
            target (str): 目标频道用户名或ID
            
        Raises:
            MessageIdInvalidError: 当消息ID无效时抛出
        """
        try:
            await event.message.forward_to(target)
        except ChatForwardsRestrictedError:
            logger.info(f"此群组不允许转发，直接提取消息将发送到: {target}")
            await self._send_message_copy(event, target)
        except Exception as e:
            logger.error(f"转发消息时发生错误: {str(e)}", exc_info=True)
            raise

    async def _send_message_copy(
        self, 
        event: events.NewMessage.Event, 
        target: str
    ) -> None:
        """发送消息副本（用于受保护聊天）
        
        Args:
            event (events.NewMessage.Event): 新消息事件对象
            target (str): 目标频道用户名或ID
            
        Raises:
            Exception: 当发送消息副本失败时抛出
        """
        try:
            await self.client.send_message(
                target,
                event.message.message,
                file=event.message.media,
                link_preview=False
            )
            logger.info(f"已发送消息副本到: {target}")
        except Exception as e:
            logger.error(f"发送消息副本到 {target} 失败: {str(e)}", exc_info=True)
            raise
