"""数据库处理模块

该模块负责处理与SQLite数据库的交互，包括消息的存储和检索
"""

import sqlite3
import os
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

# 配置日志
logger = logging.getLogger(__name__)

class DatabaseHandler:
    """数据库处理器类
    
    Attributes:
        db_path (str): 数据库文件路径
        conn (Optional[sqlite3.Connection]): 数据库连接对象
    """
    
    def __init__(self, db_path: str = 'data/messages.db') -> None:
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为'data/messages.db'
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """初始化数据库"""
        try:
            # 确保data目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 创建数据库连接
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"数据库已初始化，路径: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise RuntimeError("数据库初始化失败") from e

    def _create_tables(self) -> None:
        """创建必要的数据表
        
        Raises:
            RuntimeError: 当创建表失败时抛出
        """
        try:
            with self._get_cursor() as cursor:
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
            logger.info("数据表已创建/验证")
        except Exception as e:
            logger.error(f"创建数据表失败: {str(e)}")
            raise RuntimeError("创建数据表失败") from e

    @contextmanager
    def _get_cursor(self):
        """获取数据库游标的上下文管理器
        
        Yields:
            sqlite3.Cursor: 数据库游标对象
            
        Raises:
            ConnectionError: 当数据库未连接时抛出
        """
        if not self.conn:
            raise ConnectionError("数据库未连接")
            
        cursor = self.conn.cursor()
        try:
            yield cursor
        except Exception as e:
            self.conn.rollback()
            logger.error(f"数据库操作失败: {str(e)}")
            raise
        finally:
            cursor.close()

    def save_message(self, data: Dict[str, Any]) -> None:
        """保存消息数据到数据库
        
        Args:
            data: 包含消息数据的字典
            
        Raises:
            ValueError: 当输入数据无效时抛出
            RuntimeError: 当保存消息失败时抛出
        """
        try:
            if not data or not isinstance(data, dict):
                raise ValueError("无效的消息数据")
                
            required_fields = ['user_id', 'chat_id', 'date']
            if not all(field in data for field in required_fields):
                raise ValueError(f"消息数据缺少必要字段: {required_fields}")
                
            with self._get_cursor() as cursor:
                sql = '''
                INSERT INTO messages (
                    username, first_name, last_name, user_id,
                    chat_type, chat_title, chat_id, message,
                    date, is_bot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                values = (
                    data.get('username', '否'),
                    data.get('first_name', '否'),
                    data.get('last_name', '否'),
                    data['user_id'],
                    data.get('chat_type', '否'),
                    data.get('chat_title', '否'),
                    data['chat_id'],
                    data.get('message', '否'),
                    data['date'],
                    1 if data.get('is_bot') else 0
                )
                
                cursor.execute(sql, values)
                self.conn.commit()
                logger.info(f"消息已保存: user_id={data['user_id']}")
        except ValueError as e:
            logger.error(f"无效的消息数据: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"保存消息失败: {str(e)}")
            raise RuntimeError("保存消息失败") from e

    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("数据库连接已关闭")

# 创建全局数据库处理器实例
db = DatabaseHandler()
