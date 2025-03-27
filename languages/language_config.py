"""
Language configuration module for System Safety Tools.
Provides multi-language support with dynamic language switching capabilities.
"""

import os
import locale
import json
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Configure basic logging for module-level initialization
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Language(Enum):
    """
    Supported languages enum.
    Each value represents the language code used for localization.
    """
    CHINESE = "zh"
    ENGLISH = "en"

    @classmethod
    def from_string(cls, lang_str: str) -> 'Language':
        """Convert a string to a Language enum value."""
        try:
            # Find the enum value that matches the string
            return next(lang for lang in cls if lang.value == lang_str)
        except StopIteration:
            # Default to system locale if not found
            return cls.from_system_locale()

    @classmethod
    def from_system_locale(cls) -> 'Language':
        """Determine language from system locale."""
        try:
            # Get the system locale
            system_locale, _ = locale.getdefaultlocale()
            
            # Extract language code from locale
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                
                # Map the language code to our supported languages
                if lang_code == "zh":
                    return cls.CHINESE
                # Add more language mappings as needed
            
            # Default to English if locale not recognized or supported
            return cls.ENGLISH
            
        except Exception as e:
            logger.error(f"Error determining system locale: {e}")
            return cls.ENGLISH

class LanguageStrings:
    """
    Container for language string definitions.
    Provides string dictionaries for each supported language.
    """
    # Default language strings will be populated during initialization
    CHINESE: Dict[str, str] = {}
    ENGLISH: Dict[str, str] = {}
    
    # Dictionary mapping language codes to string dictionaries
    STRINGS: Dict[str, Dict[str, str]] = {}
    
    @classmethod
    def load_from_file(cls, file_path: str) -> bool:
        """
        Load language strings from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing language strings
            
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Language file not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
                
            # Update language dictionaries
            for lang_code, strings in lang_data.items():
                if lang_code == "zh":
                    cls.CHINESE.update(strings)
                elif lang_code == "en":
                    cls.ENGLISH.update(strings)
                    
            # Update the STRINGS dictionary
            cls.STRINGS = {
                "zh": cls.CHINESE,
                "en": cls.ENGLISH
            }
            
            logger.info(f"Loaded language strings from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading language file {file_path}: {e}")
            return False
    
    @classmethod
    def save_to_file(cls, file_path: str) -> bool:
        """
        Save language strings to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Prepare data to save
            lang_data = {
                "zh": cls.CHINESE,
                "en": cls.ENGLISH
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Saved language strings to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving language file {file_path}: {e}")
            return False
    
    @classmethod
    def get_strings_for_language(cls, language: Language) -> Dict[str, str]:
        """Get the string dictionary for a specific language."""
        lang_code = language.value
        return cls.STRINGS.get(lang_code, cls.ENGLISH)  # Default to English if not found

class LanguageManager:
    """
    Language manager singleton class.
    Handles language selection and string retrieval.
    """
    _instance = None
    _current_language = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LanguageManager._initialized:
            self._initialize()
            LanguageManager._initialized = True
    
    def _initialize(self):
        """Initialize the language manager."""
        try:
            # Set default language based on system locale
            LanguageManager._current_language = Language.from_system_locale()
            
            # Ensure the STRINGS dictionary is initialized
            if not hasattr(LanguageStrings, 'STRINGS') or not LanguageStrings.STRINGS:
                LanguageStrings.STRINGS = {
                    "zh": LanguageStrings.CHINESE,
                    "en": LanguageStrings.ENGLISH
                }
                
            logger.info(f"Language manager initialized with language: {LanguageManager._current_language.value}")
            
        except Exception as e:
            logger.error(f"Error initializing language manager: {e}")
            # Fall back to English in case of error
            LanguageManager._current_language = Language.ENGLISH
    
    @classmethod
    def set_language(cls, language: Language) -> None:
        """
        Set the current language.
        
        Args:
            language: The Language enum value to set as current
        """
        if not isinstance(language, Language):
            logger.warning(f"Invalid language type: {type(language)}. Expected Language enum.")
            return
            
        cls._current_language = language
        logger.info(f"Language set to: {language.value}")
    
    @classmethod
    def get_current_language(cls) -> Language:
        """Get the current language."""
        if cls._current_language is None:
            # Initialize if not already done
            _ = cls()
        return cls._current_language
    
    @classmethod
    def get_string(cls, key: str, default: Optional[str] = None) -> str:
        """
        Get a localized string by key.
        
        Args:
            key: The string identifier
            default: Default value to return if key not found
            
        Returns:
            str: The localized string or default/key if not found
        """
        if cls._current_language is None:
            # Initialize if not already done
            _ = cls()
            
        # Get the appropriate string dictionary
        strings = LanguageStrings.get_strings_for_language(cls._current_language)
        
        # Look up the string
        if key in strings:
            return strings[key]
        elif default is not None:
            logger.warning(f"String key not found: {key}, using default")
            return default
        else:
            logger.warning(f"String key not found: {key}, using key as value")
            return key

def init_language_strings():
    """
    Initialize built-in language strings.
    This function populates the default strings for each supported language.
    """
    # Chinese strings (simplified)
    chinese_strings = {
        "title": "Windows系统健康检查与修复",
        "functions": "功能列表",
        "output_text": "输出信息",
        "clear_output": "清除输出",
        "help_title": "帮助信息",
        "dark_mode": "深色模式",
        "light_mode": "明亮模式",
        "settings": "设置",
        "language": "语言",
        "apply": "应用",
        "cancel": "取消",
        "exit": "退出",
        "confirm": "确认",
        "warning": "警告",
        "error": "错误",
        "success": "成功",
        "information": "信息",
        
        # Menu items
        "menu_items": [
            "系统文件检查", 
            "清理无用文件", 
            "显示GPU信息",
            "系统检查与清理", 
            "Windows DISM工具", 
            "网络套接字重置", 
            "驱动器检查", 
            "修复引导", 
            "病毒扫描"
        ],
        
        # Settings
        "current_language": "当前语言",
        "set_chinese": "设置为中文",
        "set_english": "设置为英文",
        "language_changed": "语言已更改",
        "restart_needed": "需要重启程序以完全应用语言更改",
        "theme_settings": "界面主题",
        "file_extension_settings": "文件后缀设置",
        "exclude_settings": "排除设置",
        "exclude_files_folders": "排除的文件和文件夹",
        "exclude_description": "这些文件或文件夹不会被清理功能处理",
        "add_file": "添加文件",
        "add_folder": "添加文件夹",
        "remove_item": "移除项目",
        "select_file_to_exclude": "选择要排除的文件",
        "select_folder_to_exclude": "选择要排除的文件夹",
        "settings_title": "设置",
        "return_text": "返回",
        "language_changed_zh": "语言已更改为中文",
        "language_changed_en": "语言已更改为英文",
        "already_chinese": "当前已经是中文",
        "already_english": "当前已经是英文",
        "no_drives_detected": "未检测到驱动器",
        "readonly_mode_prompt": "是否以只读模式检查? (y/n)",
        "readonly_mode_check": "只读模式检查",
        "repair_mode_check": "修复模式检查",
        "driver_check_tool_init": "驱动器检查工具初始化",
        "checking_all_drives": "正在检查所有驱动器",
        "error_occurred": "发生错误: ",
        "select_drive": "选择驱动器",
        "enter_drive_letter": "请输入驱动器盘符(例如: C): ",
        "network_reset_warning": "网络重置警告",
        "confirm_network_reset": "确认要重置网络? 这可能会暂时断开网络连接。",
        "confirm_y_n": "确认(y/n): ",
        "network_reset_completed": "网络重置完成",
        "restart_required": "需要重启计算机以应用更改",
        "network_reset_timeout": "网络重置命令超时",
        "network_reset_failed": "网络重置失败",
        "network_command_not_found": "未找到网络命令",
        "network_permission_denied": "没有权限执行网络重置",
        "run_as_administrator": "请以管理员身份运行",
        "unexpected_error": "未预期的错误",
        "virus_scan_title": "病毒扫描",
        "scan_options": "扫描选项:",
        "quick_scan_option": "1. 快速扫描",
        "full_scan_option": "2. 完整扫描",
        "custom_scan_option": "3. 自定义路径扫描",
        "update_defs_option": "4. 更新病毒定义",
        "enter_custom_path": "输入自定义路径: ",
        "gpu_error": "GPU错误",
        "sfc_no_violations": "系统文件检查器未发现任何完整性违规",
        "sfc_completed_violations": "系统文件检查器发现并修复了一些文件完整性问题",
        "fix_system_integrity": "是否要修复系统完整性? (y/n): ",
        "sfc_not_found": "找不到系统文件检查器(SFC)命令",
        "sfc_permission_denied": "没有权限执行系统文件检查",
        "subprocess_error": "子进程错误",
        "chkdsk_timeout": "磁盘检查操作超时",
        "chkdsk_error": "磁盘检查错误",
        "bootrec_specify_action": "请指定bootrec操作（如/fixmbr, /fixboot, /rebuildbcd）",
        "bootrec_completed": "引导修复完成",
        "bootrec_error": "引导修复错误",
        "system_image_repair_complete": "系统映像修复完成",
        "dism_timeout": "DISM操作超时",
        "system_health_scan_complete": "系统健康扫描完成",
        "no_corruption_detected": "未检测到损坏",
        "system_image_repair_error": "系统映像修复错误",
        "dism_health_check_error": "DISM健康检查错误",
        "gpu_command_timeout": "GPU信息命令超时",
        "gpu_not_found": "未找到GPU",
        "gpu_command_not_found": "找不到GPU命令",
        "gpu_permission_denied": "没有权限获取GPU信息",
        "system_cleanup_error": "系统清理错误",
        "operation_timeout": "操作超时",
        "no_write_permission": "没有写入权限",
        "deleted": "已删除",
        "permission_error": "权限错误",
        "file_not_found": "文件未找到",
        "os_error": "操作系统错误",
        "permission_error_drive": "访问驱动器时出现权限错误",
        "os_error_drive": "访问驱动器时出现系统错误",
        "unexpected_error_drive": "访问驱动器时出现未预期错误",
        "removed": "已移除",
        "remove_failed": "移除失败",
        "recycle_bin_cleaned": "回收站已清空",
        "recycle_bin_clean_failed": "清空回收站失败",
        "access_recycle_bin_error": "访问回收站错误",
        "cleaning_temp_files": "正在清理临时文件",
        "cleaning_log_files": "正在清理日志文件",
        "running_sfc_scannow": "正在运行系统文件检查器(sfc /scannow)...",
        "please_wait": "请耐心等待，这可能需要一些时间...",
        "sfc_failed": "系统文件检查失败",
        "error_details": "错误详情",
        "help_input_number": "输入数字选择对应功能",
        "help_esc_exit": "按ESC键退出当前操作",
        "help_settings": "在设置中可以切换界面主题",
        "normal_display_mode": "1. 普通显示模式",
        "continuous_display_mode": "2. 连续显示模式",
        "dism_auto_option": "1. 自动检查并修复系统映像",
        "dism_manual_option": "2. 手动修复系统映像",
        "check_single_drive": "1. 检查单个驱动器",
        "check_all_drives": "2. 检查所有驱动器",
        "admin_required": "需要管理员权限",
        "run_as_admin": "此操作需要管理员权限才能执行。\n请右键点击程序，选择\"以管理员身份运行\"后重试。",
        "continue_anyway": "是否仍要继续？",
        "select_option": "请选择选项:",
        "specify_bootrec_operation": "请指定要执行的引导修复操作:",
        "enter_choice": "请输入选择:",
        "operation_failed": "操作失败",
        "invalid_choice": "无效的选择，请重试",
        "press_esc": "按ESC键返回",
        "press_any_key": "按任意键继续...",
        "input_cancelled": "输入已取消",
        "operation_cancelled": "操作已取消",
        "input_error": "输入错误",
        "add_extension": "添加后缀",
        "remove_extension": "移除后缀",
        "default_extensions": "恢复默认",
        "current_extensions": "当前清理的文件后缀",
        "enter_extension": "请输入文件后缀(不含点，例如: log)",
        "extension_added": "已添加后缀",
        "extension_removed": "已移除后缀",
        "extensions_reset": "已恢复默认后缀设置",
        "settings_saved": "设置已保存",
        "virus_scan_starting": "正在开始病毒扫描...",
        "quick_scan_info": "执行快速扫描将检查系统关键区域",
        "full_scan_info": "执行完整扫描将检查整个系统",
        "full_scan_warning": "完整扫描可能需要较长时间",
        "quick_scan_completed": "快速扫描完成",
        "full_scan_completed": "完整扫描完成",
        "custom_scan_completed": "自定义扫描完成",
        "scan_failed": "扫描失败",
        "scan_timeout": "扫描超时",
        "defender_not_found": "未找到Windows Defender命令",
        "defender_permission_denied": "没有权限运行Windows Defender扫描",
        "custom_scan_path": "自定义扫描路径",
        "invalid_path": "无效的路径",
        "updating_definitions": "正在更新病毒定义...",
        "definitions_updated": "病毒定义已更新",
        "update_failed": "更新失败",
        "update_timeout": "更新超时",
        "threats_detected": "检测到威胁",
        "no_threats_detected": "未检测到威胁",
        "remove_threats_prompt": "是否要移除检测到的威胁?",
        "removing_threats": "正在移除威胁...",
        "threats_removed": "威胁已移除",
        "removal_failed": "移除失败",
        "removal_timeout": "移除超时",
        "results_error": "显示结果时出错",
        "input_timeout": "输入超时",
        "window_title_new_tool": "工具 - {0}",  # 新窗口的标题格式
        "press_esc_to_stop": "按ESC键停止监控",
        "confirm_check_all_drives": "确认要检查所有驱动器吗？这可能需要较长时间。",
        "drive_check_cancelled": "驱动器检查已取消",
        "select_language": "选择语言",
        "select_theme": "选择主题",
        "theme_customization": "主题自定义",
        "theme_mode": "主题模式",
        "primary_color": "主色调",
        "accent_color": "强调色",
        "background_color": "背景色",
        "card_color": "卡片背景色",
        "text_color": "文本颜色",
        "select_color": "选择颜色",
        "theme_preview": "主题预览",
        "reset_to_default": "重置为默认",
        "theme_applied": "主题已应用",
        "theme_settings": "主题设置"
    }
    
    # English strings
    english_strings = {
        "title": "Windows System Health Check & Repair",
        "functions": "Functions",
        "output_text": "Output",
        "clear_output": "Clear Output",
        "help_title": "Help",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "settings": "Settings",
        "language": "Language",
        "apply": "Apply",
        "cancel": "Cancel",
        "exit": "Exit",
        "confirm": "Confirm",
        "warning": "Warning",
        "error": "Error",
        "help_input_number": "Enter a number to select a function",
        "help_esc_exit": "Press ESC to exit current operation",
        "help_settings": "You can change theme in settings",
        
        # 工具相关字符串
        "running_sfc_scannow": "Running system file checker (sfc /scannow)...",
        "please_wait": "Please wait, this may take some time...",
        "sfc_failed": "System file check failed",
        "error_details": "Error Details",
        "removed": "Removed",
        "confirm_action": "Confirm this action?",
        "current_language": "Current Language",
        "set_chinese": "Set to Chinese",
        "set_english": "Set to English",
        "language_changed": "Language Changed",
        "restart_needed": "Restart required to fully apply language changes",
        
        # 文件后缀设置
        "file_extension_settings": "File Extension Settings",
        "add_extension": "Add Extension",
        "remove_extension": "Remove Extension",
        "default_extensions": "Reset to Default",
        "current_extensions": "Current Extensions to Clean",
        "enter_extension": "Enter file extension (without dot, e.g. log)",
        "extension_added": "Extension Added",
        "extension_removed": "Extension Removed",
        "extensions_reset": "Extensions Reset to Default",
        "settings": "Settings",
        
        # Menu items
        "menu_items": [
            "System File Check", 
            "Clean Unused Files", 
            "Display GPU Info",
            "System Check & Clean", 
            "Windows DISM Tools", 
            "Network Socket Reset", 
            "Drive Check", 
            "Boot Repair", 
            "Virus Scan"
        ],
        
        # Settings
        "current_language": "Current Language",
        "set_chinese": "Set to Chinese",
        "set_english": "Set to English",
        "language_changed": "Language Changed",
        "restart_needed": "Restart required to fully apply language changes",
        "theme_settings": "UI Theme",
        "file_extension_settings": "File Extension Settings",
        "exclude_settings": "Exclusion Settings",
        "exclude_files_folders": "Excluded Files and Folders",
        "exclude_description": "These files or folders will not be processed by cleanup functions",
        
        "press_esc_to_stop": "Press ESC to stop monitoring",
        "confirm_check_all_drives": "Confirm checking all drives? This may take a while.",
        "drive_check_cancelled": "Drive check cancelled",
        "select_language": "Select Language",
        "select_theme": "Select Theme",
        "theme_customization": "Theme Customization",
        "theme_mode": "Theme Mode",
        "primary_color": "Primary Color",
        "accent_color": "Accent Color",
        "background_color": "Background Color",
        "card_color": "Card Background",
        "text_color": "Text Color",
        "select_color": "Select Color",
        "theme_preview": "Theme Preview",
        "reset_to_default": "Reset to Default",
        "theme_applied": "Theme Applied",
        "theme_settings": "Theme Settings"
    }
    
    LanguageStrings.CHINESE.update(chinese_strings)
    LanguageStrings.ENGLISH.update(english_strings)
    
    LanguageStrings.STRINGS = {
        "zh": LanguageStrings.CHINESE,
        "en": LanguageStrings.ENGLISH
    }

    logger.info("Built-in language strings initialized")
    
    lang_file = Path("config/language_strings.json")
    if lang_file.exists():
        LanguageStrings.load_from_file(str(lang_file))

init_language_strings() 