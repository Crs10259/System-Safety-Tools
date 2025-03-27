import os
import time
import msvcrt
from tools import *
from typing import List, Callable
from languages.language_config import LanguageManager, Language
from log_utils import LogManager
from config.settings_manager import SettingsManager

class ApplyConfig:
    @property
    def TITLE(self):
        return LanguageManager.get_string("title")
        
    VERSION = '1.0.1'
    DEBUG_MODE = False

class ApplyTools:
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

def show_settings():
    """显示和管理设置选项"""
    logger = LogManager().get_logger(__name__)
    settings_manager = SettingsManager()
    
    while True:
        os.system('cls')
        current_lang = LanguageManager.get_current_language()
        
        print(f"======== {LanguageManager.get_string('settings_title')} ========\n")
        print(f"{LanguageManager.get_string('current_language')}: {current_lang.value}\n")
        print(f"1. {LanguageManager.get_string('set_chinese')}")
        print(f"2. {LanguageManager.get_string('set_english')}")
        print(f"ESC. {LanguageManager.get_string('return_text')}")
        
        choice = msvcrt.getch()
        
        if choice == b'\x1b': 
            break
            
        if choice.decode() == '1':
            if current_lang != Language.CHINESE:
                LanguageManager.set_language(Language.CHINESE)
                settings_manager.save_settings()
                logger.info("Language changed to Chinese")
                print(f"\n{LanguageManager.get_string('language_changed_zh')}")
                time.sleep(1.5)
                break
            else:
                print(f"\n{LanguageManager.get_string('already_chinese')}")
                time.sleep(1.5)
                
        elif choice.decode() == '2':
            if current_lang != Language.ENGLISH:
                LanguageManager.set_language(Language.ENGLISH)
                settings_manager.save_settings()
                logger.info("Language changed to English")
                print(f"\n{LanguageManager.get_string('language_changed_en')}")
                time.sleep(1.5)
                break
            else:
                print(f"\n{LanguageManager.get_string('already_english')}")
                time.sleep(1.5)
