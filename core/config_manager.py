import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

class ConfigManager:
    """统一配置管理类
    
    Attributes:
        config_path (Path): 配置文件路径
        _config (Dict[str, Any]): 配置数据字典
        logger (Logger): 日志记录器
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """初始化配置管理器
        
        Args:
            config_path (Optional[str]): 自定义配置文件路径，默认为None
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent / 'config/config.json'
        else:
            self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件
        
        Raises:
            FileNotFoundError: 当配置文件不存在时抛出
            json.JSONDecodeError: 当配置文件格式错误时抛出
            Exception: 其他加载失败时抛出
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self.logger.info(f"配置文件加载成功: {self.config_path}")
        except FileNotFoundError as e:
            self.logger.error(f"配置文件不存在: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {self.config_path}")
            raise
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}", exc_info=True)
            raise
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """安全获取配置项
        
        Args:
            key (str): 配置项键名
            default (Optional[Any]): 默认值，当键不存在时返回
            
        Returns:
            Any: 配置项值或默认值
        """
        return self._config.get(key, default)
    
    def reload(self) -> None:
        """重新加载配置文件
        
        Raises:
            Exception: 当重新加载失败时抛出
        """
        try:
            self.load_config()
            self.logger.info("配置文件重新加载成功")
        except Exception as e:
            self.logger.error(f"重新加载配置文件失败: {str(e)}", exc_info=True)
            raise
    
    @property
    def api_id(self) -> int:
        """获取Telegram API ID
        
        Returns:
            int: API ID
            
        Raises:
            ValueError: 当API ID无效时抛出
        """
        try:
            return int(self.get('API_ID'))
        except (TypeError, ValueError) as e:
            self.logger.error(f"无效的API ID: {self.get('API_ID')}")
            raise ValueError("无效的API ID") from e
    
    @property
    def api_hash(self) -> str:
        """获取Telegram API Hash
        
        Returns:
            str: API Hash
            
        Raises:
            ValueError: 当API Hash无效时抛出
        """
        api_hash = self.get('API_HASH')
        if not api_hash or not isinstance(api_hash, str):
            self.logger.error(f"无效的API Hash: {api_hash}")
            raise ValueError("无效的API Hash")
        return str(api_hash)
    
    @property
    def blocked_chat_ids(self) -> List[int]:
        """获取屏蔽的聊天ID列表
        
        Returns:
            List[int]: 屏蔽的聊天ID列表
            
        Raises:
            ValueError: 当ID格式无效时抛出
        """
        try:
            return [int(chat_id) for chat_id in self.get('blocked_chat_ids', [])]
        except (TypeError, ValueError) as e:
            self.logger.error(f"无效的聊天ID格式: {self.get('blocked_chat_ids')}")
            raise ValueError("无效的聊天ID格式") from e

    @property
    def target_channel(self) -> str:
        """获取主转发目标频道
        
        Returns:
            str: 目标频道用户名或ID
            
        Raises:
            ValueError: 当目标频道无效时抛出
        """
        target = self.get('target_channel', '')
        if not target:
            self.logger.error("未配置目标频道")
            raise ValueError("未配置目标频道")
        return str(target)
    
    @property
    def patterns(self) -> List[Dict[str, Any]]:
        """获取消息匹配模式
        
        Returns:
            List[Dict[str, Any]]: 消息匹配模式列表
            
        Raises:
            FileNotFoundError: 当patterns.json文件不存在时抛出
            json.JSONDecodeError: 当patterns.json格式错误时抛出
            Exception: 其他加载失败时抛出
        """
        patterns_path = Path(__file__).parent.parent / 'config/patterns.json'
        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
                if not isinstance(patterns, list):
                    raise ValueError("patterns.json格式错误：应为列表")
                return patterns
        except FileNotFoundError as e:
            self.logger.error(f"patterns.json文件不存在: {patterns_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"patterns.json格式错误: {patterns_path}")
            raise
        except Exception as e:
            self.logger.error(f"加载patterns.json失败: {str(e)}", exc_info=True)
            raise

    @property
    def blocked_chat_ids(self) -> List[int]:
        """获取屏蔽的聊天ID列表
        
        Returns:
            List[int]: 屏蔽的聊天ID列表
            
        Raises:
            ValueError: 当ID格式无效时抛出
        """
        try:
            return [int(chat_id) for chat_id in self.get('blocked_chat_ids', [])]
        except (TypeError, ValueError) as e:
            self.logger.error(f"无效的聊天ID格式: {self.get('blocked_chat_ids')}")
            raise ValueError("无效的聊天ID格式") from e

# 创建全局配置管理器实例
config_manager: ConfigManager = ConfigManager()
