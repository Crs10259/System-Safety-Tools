import json
import os
from pathlib import Path
from languages.language_config import Language, LanguageManager
from log_utils import LogManager

class SettingsManager:
    """配置管理器类"""
    
    _instance = None
    _config_dir = Path("config")
    _config_file = _config_dir / "settings.json"
    _logger = LogManager().get_logger(__name__)
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化配置目录和文件"""
        try:
            # 确保配置目录存在
            self._config_dir.mkdir(exist_ok=True)
            
            # 如果配置文件不存在，创建默认配置
            if not self._config_file.exists():
                self._create_default_config()
            
            # 加载配置
            self.load_settings()
            
        except Exception as e:
            self._logger.error(f"初始化配置管理器失败: {str(e)}")
            # 如果出错，使用系统默认语言
            LanguageManager.set_language(Language.from_system_locale())
    
    def _create_default_config(self):
        """创建默认配置文件时使用系统语言"""
        default_settings = {
            "language": Language.from_system_locale().value
        }
        
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=4, ensure_ascii=False)
                
            self._logger.info("创建默认配置文件")
            
        except Exception as e:
            self._logger.error(f"创建默认配置文件失败: {str(e)}")
    
    def load_settings(self):
        """加载配置设置"""
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 设置语言
            language_value = settings.get('language', 'zh')
            language = next((lang for lang in Language if lang.value == language_value), 
                          Language.from_system_locale())
            
            LanguageManager.set_language(language)
            self._logger.info(f"已加载语言设置: {language.value}")
            
        except Exception as e:
            self._logger.error(f"加载配置文件失败: {str(e)}")
            # 如果出错，使用系统默认语言
            LanguageManager.set_language(Language.from_system_locale())
    
    def save_settings(self):
        """保存当前设置到配置文件"""
        try:
            current_language = LanguageManager.get_current_language()
            settings = {
                "language": current_language.value
            }
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
                
            self._logger.info(f"已保存语言设置: {current_language.value}")
            
        except Exception as e:
            self._logger.error(f"保存配置文件失败: {str(e)}") 