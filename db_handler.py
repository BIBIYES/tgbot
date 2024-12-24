import sqlite3
from datetime import datetime
import os

class DatabaseHandler:
    def __init__(self):
        """初始化数据库连接"""
        # 确保data目录存在
        if not os.path.exists('data'):
            os.makedirs('data')
        
        self.db_path = 'data/messages.db'
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
    
    def create_tables(self):
        """创建必要的数据表"""
        cursor = self.conn.cursor()
        
        # 创建消息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT DEFAULT '否',
            first_name TEXT DEFAULT '否',
            last_name TEXT DEFAULT '否',
            user_id INTEGER,
            chat_type TEXT DEFAULT '否',
            chat_title TEXT DEFAULT '否',
            chat_id INTEGER,
            message TEXT DEFAULT '否',
            date TIMESTAMP,
            is_bot INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    def save_message(self, data):
        """保存消息数据到数据库"""
        cursor = self.conn.cursor()
        
        # 准备SQL语句
        sql = '''
        INSERT INTO messages (
            username, first_name, last_name, user_id,
            chat_type, chat_title, chat_id, message,
            date, is_bot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        # 准备数据，如果值为None则使用'否'
        values = (
            data.get('username', '否'),
            data.get('first_name', '否'),
            data.get('last_name', '否'),
            data.get('user_id'),
            data.get('chat_type', '否'),
            data.get('chat_title', '否'),
            data.get('chat_id'),
            data.get('message', '否'),
            data.get('date'),
            1 if data.get('is_bot') else 0
        )
        
        cursor.execute(sql, values)
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

# 创建全局数据库处理器实例
db = DatabaseHandler()
