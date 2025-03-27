"""
Configuration management module for System Safety Tools
包含系统配置管理相关的模块和类
"""

from .settings_manager import SettingsManager

__all__ = [
    'SettingsManager'
]

# 版本信息
__version__ = '1.0.0'

# 模块说明
__doc__ = """
配置管理模块
============

这个模块提供了系统配置的管理功能，包括：
- 语言设置的保存和加载
- 配置文件的管理
- 系统设置的持久化

主要组件：
- SettingsManager: 配置管理器类，负责处理所有配置相关的操作

使用示例：
    from config import SettingsManager
    
    # 获取配置管理器实例
    settings = SettingsManager()
    
    # 保存设置
    settings.save_settings()
    
    # 加载设置
    settings.load_settings()
"""
