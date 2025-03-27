"""
Language support module for System Safety Tools
系统安全工具的语言支持模块

This module provides multi-language support for the application, including:
- Language configuration management
- String localization
- Dynamic language switching
"""

from .language_config import (
    Language,
    LanguageManager,
    init_language_strings
)

__all__ = [
    'Language',
    'LanguageManager',
    'init_language_strings'
]

# 版本信息
__version__ = '1.0.0'

# 支持的语言列表
SUPPORTED_LANGUAGES = {
    'zh': '简体中文',
    'en': 'English'
}

# 模块说明
__doc__ = """
语言支持模块
===========

这个模块提供了应用程序的多语言支持功能，包括：

1. 语言配置管理
   - 支持动态切换语言
   - 自动检测系统语言
   - 持久化语言设置

2. 字符串本地化
   - 中文支持
   - 英文支持
   - 可扩展的语言字符串管理

3. 主要组件：
   - Language: 语言枚举类，定义支持的语言
   - LanguageStrings: 语言字符串配置类
   - LanguageManager: 语言管理器类，处理语言切换和字符串获取

使用示例：
    from languages import LanguageManager, Language
    
    # 获取当前语言
    current_lang = LanguageManager.get_current_language()
    
    # 切换语言
    LanguageManager.set_language(Language.ENGLISH)
    
    # 获取本地化字符串
    title = LanguageManager.get_string("title")

注意事项：
1. 确保在使用字符串前初始化 LanguageManager
2. 使用 get_string 方法获取本地化字符串
3. 语言切换会立即生效
"""

# 初始化说明
def initialize():
    """
    初始化语言支持模块
    - 检测系统语言
    - 加载默认语言设置
    - 初始化语言管理器
    """
    # 创建LanguageManager实例以触发其初始化逻辑
    from .language_config import init_language_strings
    init_language_strings()
    _ = LanguageManager()

# 模块初始化时自动执行
initialize()    
