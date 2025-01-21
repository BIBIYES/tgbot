"""Telegram 机器人主程序

该模块负责初始化并运行 Telegram 机器人
"""

import logging
from typing import NoReturn
from core.Tgbot import Tgbot
from core.config_manager import config_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main() -> NoReturn:
    """主程序入口
    
    Raises:
        SystemExit: 当程序异常退出时抛出
    """
    try:
        logger.info("正在初始化机器人...")
        bot = Tgbot(
            api_id=config_manager.api_id,
            api_hash=config_manager.api_hash,
        )
        logger.info("机器人初始化成功")
        
        logger.info("启动机器人...")
        bot.run()
    except Exception as e:
        logger.critical(f"机器人运行失败: {str(e)}", exc_info=True)
        raise SystemExit(1) from e

if __name__ == "__main__":
    main()
