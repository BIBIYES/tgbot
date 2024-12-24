from telethon import TelegramClient, events  # Telethon核心库，用于Telegram客户端功能
from messageTools import message_handler
class Tgbot:
    """
    Telegram机器人类
    用于创建和管理Telegram客户端连接
    支持会话持久化和基本的客户端操作
    """
    def __init__(self, api_id: int, api_hash: str):
        """
        初始化Telegram客户端
        参数:
            api_id: 从my.telegram.org获取的API ID
            api_hash: 从my.telegram.org获取的API hash
        """
        self.api_id = api_id
        self.api_hash = api_hash
        # 创建客户端实例，如果提供了session_string则使用它，否则创建新会话
        self.client = TelegramClient(
            "my_bot_session",  # session name
            self.api_id,
            self.api_hash
        )   
    
        
    
    async def start(self):
       
        """
        启动客户端并处理登录流程
        - 如果未授权，会要求输入手机号和验证码
        - 如果使用StringSession，会打印会话字符串供将来使用
        """
        await self.client.start()
        if not await self.client.is_user_authorized():
            # 获取用户输入的手机号
            phone = input('请输入你的手机号 (格式如: +8613812345678): ')
            # 发送验证码到手机
            await self.client.send_code_request(phone)
            # 等待用户输入验证码
            await self.client.sign_in(phone, input('请输入验证码: '))
        
        
        async def handle_message(event):
            """
            处理接收到的消息事件
            参数:
                event: Telegram事件对象，包含消息信息
            """
            message_handler(event)
            
        # 监听客户端的消息事件
        self.client.add_event_handler(handle_message, events.NewMessage())
    
    
    async def stop(self):
        """
        停止客户端连接
        安全地断开与Telegram服务器的连接
        """
        await self.client.disconnect()

    def run(self):
        """
        运行机器人的主方法
        - 启动客户端
        - 保持运行直到被中断
        - 处理键盘中断信号，实现优雅退出
        """
        try:
            print("正在启动Telegram机器人...")
            self.client.loop.run_until_complete(self.start())
            print("机器人已成功运行...")
            self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            print("\n正在停止机器人...")
            self.client.loop.run_until_complete(self.stop())
            print("机器人已成功停止！")
        