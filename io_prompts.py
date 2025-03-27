"""GUI 模式的 IO 处理模块"""
import tkinter as tk
import os
import msvcrt
from typing import Callable, Any
from functools import wraps
import threading
from config.timeout_config import TimeoutConfig
from languages.language_config import LanguageManager

# 添加一个全局变量以判断是否在GUI模式下运行
IN_GUI_MODE = False

# 全局变量用于保存主窗口引用
ROOT_WINDOW = None

def set_gui_mode(mode=True):
    """设置当前运行环境是否为GUI模式"""
    global IN_GUI_MODE
    IN_GUI_MODE = mode

def set_root_window(window):
    """设置应用程序主窗口引用"""
    global ROOT_WINDOW
    ROOT_WINDOW = window

def get_root_window():
    """获取应用程序主窗口引用"""
    global ROOT_WINDOW
    return ROOT_WINDOW

def confirm_action(prompt: str = None) -> bool:
    """获取用户对操作的确认"""
    global IN_GUI_MODE
    
    if prompt is None:
        prompt = LanguageManager.get_string("confirm_action")
    
    # 检查是否在GUI模式下运行
    if IN_GUI_MODE:
        # 在GUI模式下，会被ui_interface中的ConfirmDialog处理
        print(prompt)
        # 默认返回True，实际确认由GUI处理
        return True
    else:
        # 传统命令行模式
        print(prompt)
        return msvcrt.getch().decode().lower() == "y"

def clear_screen():
    """清除控制台屏幕"""
    os.system('cls')

def wait_for_exit():
    """等待用户按ESC键退出"""
    print(LanguageManager.get_string('press_esc'))
    if msvcrt.getch() == b'\x1b':
        clear_screen()

def output(func: Callable) -> Callable:
    """
    用于需要用户确认和错误处理的函数的装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        global IN_GUI_MODE
        
        if not IN_GUI_MODE:
            clear_screen()
        
        try:
            # 在GUI模式下，确认对话框会在UI中处理
            if IN_GUI_MODE or confirm_action():
                if not IN_GUI_MODE:
                    clear_screen()
                result = func(*args, **kwargs)
                if not IN_GUI_MODE:
                    wait_for_exit()
                return result
                
        except Exception as e:
            print(f"{LanguageManager.get_string('error')}: {str(e)}")
            if not IN_GUI_MODE:
                wait_for_exit()
            
    return wrapper

def output_sleep_n(func: Callable) -> Callable:
    """
    用于需要错误处理和退出确认的函数的装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            result = func(*args, **kwargs)
            wait_for_exit()
            return result
            
        except Exception as e:
            print(f"{LanguageManager.get_string('error')}: {str(e)}")
            wait_for_exit()
            
    return wrapper

def timed_input(prompt, timeout=TimeoutConfig.get_timeout('user_input')):
    """
    带超时的输入函数
    
    参数:
        prompt: 提示文本
        timeout: 超时秒数
    
    返回:
        用户输入或None（如果超时）
    """
    result = [None]
    input_thread = None
    
    def get_input():
        result[0] = input(prompt)
    
    # 启动输入线程
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    # 等待输入或超时
    input_thread.join(timeout)
    
    # 如果线程还活着，说明超时了
    if input_thread.is_alive():
        # 打印新行，以便后续输出
        print(LanguageManager.get_string('input_timeout'))
        # 尝试取消阻塞的输入（模拟Enter键）
        msvcrt.putch(b'\r')
        return None
    
    return result[0]
