from typing import Optional
from telethon import TelegramClient, events
import asyncio
import logging
from core.config_manager import config_manager
from handlers.message_handler import MessageHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Tgbot:
    """Telegram机器人类
    
    Attributes:
        api_id (int): Telegram API ID
        api_hash (str): Telegram API Hash
        client (TelegramClient): Telegram客户端实例
        message_handler (MessageHandler): 消息处理器实例
    """

    def __init__(self, api_id: int, api_hash: str) -> None:
        """初始化Telegram客户端
        
        Args:
            api_id: 从my.telegram.org获取的API ID
            api_hash: 从my.telegram.org获取的API hash
            
        Raises:
            ValueError: 当API ID或API Hash无效时抛出
        """
        if not isinstance(api_id, int) or api_id <= 0:
            raise ValueError("无效的API ID")
        if not isinstance(api_hash, str) or not api_hash:
            raise ValueError("无效的API Hash")
            
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient(
            "my_bot_session",
            self.api_id,
            self.api_hash
        )
        self.message_handler = MessageHandler(self.client)

    async def start(self) -> None:
        """启动客户端并处理登录流程
        
        Raises:
            ConnectionError: 当连接Telegram失败时抛出
            RuntimeError: 当认证失败时抛出
        """
        try:
            logger.info("正在连接Telegram服务器...")
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                logger.info("检测到未认证用户，开始认证流程...")
                await self._handle_authentication()
            
            # 设置全局客户端实例
            from handlers.str_handler import TelegramSender
            TelegramSender.set_client(self.client)

            # 添加消息处理器
            self.client.add_event_handler(
                self.message_handler.handle_message,
                events.NewMessage()
            )
            
            logger.info("机器人启动成功，正在监听消息...")
        except ConnectionError as e:
            logger.error(f"连接Telegram服务器失败: {str(e)}")
            raise
        except RuntimeError as e:
            logger.error(f"认证流程失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"启动机器人时发生未知错误: {str(e)}", exc_info=True)
            raise

    async def _handle_authentication(self) -> None:
        """处理用户认证流程
        
        Raises:
            RuntimeError: 当认证失败时抛出
        """
        try:
            phone = input('请输入你的手机号 (格式如: +8613812345678): ')
            if not phone or not phone.startswith('+'):
                raise ValueError("无效的手机号格式")
                
            logger.info("正在发送验证码...")
            await self.client.send_code_request(phone)
            
            code = input('请输入验证码: ')
            if not code or not code.isdigit():
                raise ValueError("验证码必须为数字")
                
            logger.info("正在验证登录...")
            await self.client.sign_in(phone, code)
            logger.info("用户认证成功")
        except ValueError as e:
            logger.error(f"输入验证失败: {str(e)}")
            raise RuntimeError("认证失败：无效的输入") from e
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}", exc_info=True)
            raise RuntimeError("认证失败") from e

    async def stop(self) -> None:
        """停止客户端连接
        
        Raises:
            ConnectionError: 当断开连接失败时抛出
        """
        try:
            logger.info("正在断开Telegram连接...")
            await self.client.disconnect()
            logger.info("机器人已成功停止")
        except ConnectionError as e:
            logger.error(f"断开连接失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"停止机器人时发生未知错误: {str(e)}", exc_info=True)
            raise

    def run(self) -> None:
        """运行机器人的主方法
        
        Raises:
            SystemExit: 当程序异常退出时抛出
        """
        try:
            logger.info("正在启动Telegram机器人...")
            self.client.loop.run_until_complete(self.start())
            logger.info("机器人已成功运行，等待消息...")
            self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("\n接收到中断信号，正在停止机器人...")
            self.client.loop.run_until_complete(self.stop())
            logger.info("机器人已成功停止！")
            raise SystemExit(0)
        except Exception as e:
            logger.critical(f"机器人运行出错: {str(e)}", exc_info=True)
            raise SystemExit(1) from e
