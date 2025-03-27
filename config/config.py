import os
import time
import msvcrt
from tools import *
from typing import List, Callable
from languages.language_config import LanguageManager, Language
from log_utils import LogManager
from config.settings_manager import SettingsManager

class AppConfig:
    @property
    def TITLE(self):
        return LanguageManager.get_string("title")
        
    VERSION = '2.0.0'
    DEBUG_MODE = False

class AppTools:
    tools = [
        SystemCheckFix.sfc_scannow,
        delete_useless_files,
        gpu_basic_info,
        sfc_and_delete_useless_files,
        windows_dism_tools,
        SystemCheckFix.netsh_winsock_reset,
        CheckDriver().main,
        fix_boot,
        virus_scan
    ]
    
    @staticmethod
    def get(choice: int, app=None) -> None:
        """执行选定的工具"""
        if not 1 <= choice <= len(ApplyTools.tools):
            raise ValueError(f"无效的工具选择: {choice}")
            
        tool_func = ApplyTools.tools[choice-1]
        if hasattr(tool_func, "__wrapped__"):
            return tool_func.__wrapped__()
        else:
            return tool_func()

