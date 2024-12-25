from telethon import TelegramClient, events  # Telethon核心库，用于Telegram客户端功能
from messageTools import message_handler
import json
import asyncio  # 添加此行以支持重试机制


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

        # 设置全局客户端实例
        from strHandelr import TelegramSender
        TelegramSender.set_client(self.client)

        # 从配置文件中读取屏蔽的聊天ID列表
        with open('config.json', 'r') as f:
            config = json.load(f)
        blocked_chat_ids = config.get('blocked_chat_ids', [])

        async def handle_message(event):
            """
            处理接收到的消息事件
            参数:
                event: Telegram事件对象，包含消息信息
            """
            if event.out:
                return  # 排除自己发送的消息

            # 检查消息的聊天ID是否在屏蔽列表中
            if event.message.chat_id in blocked_chat_ids:
                print(f"消息来自屏蔽的聊天ID {event.message.chat_id}，不处理屏蔽的群组")
                return
            message_handler(event)
            try:
                # 使用频道用户名作为目标
                target_chat = 'https://t.me/center_mains'  # 替换为你的目标频道用户名

                # 重试机制
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        # 直接转发消息
                        await self.client.forward_messages(
                            target_chat,
                            messages=event.message
                        )
                        break  # 成功后退出循环
                    except Exception as e:
                        print(f"转发消息时出错: {str(e)}，重试 {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                        else:
                            raise e  # 达到最大重试次数后抛出异常

            except Exception as e:
                print(f"转发消息时出错: {str(e)}")

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
