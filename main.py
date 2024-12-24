from Tgbot import Tgbot
import json


# 从 json 中 读取配置文件
with open('config.json', 'r') as f:
    config = json.load(f)
API_ID=(config['API_ID'])
API_HASH=(config['API_HASH'])
# 初始化机器人

bot = Tgbot(
    api_id=API_ID,
    api_hash=API_HASH,
)

if __name__ == "__main__":
    # 运行机器人
    bot.run()