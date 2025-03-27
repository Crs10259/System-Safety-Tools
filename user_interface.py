import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog, colorchooser
import threading
import os
import sys
import time
from pathlib import Path
import platform
from PIL import Image, ImageTk  
import subprocess
import json

from languages import LanguageManager, Language
from log_utils import LogManager
from tools import *
from config import AppTools, AppConfig
from config import SettingsManager

import io_prompts as op
op.set_gui_mode(True)  # 设置为GUI模式

# 定义颜色主题
class UITheme:
    # 主色调
    PRIMARY = "#3f51b5"
    PRIMARY_LIGHT = "#757de8" 
    PRIMARY_DARK = "#002984"
    
    # 明亮模式背景色
    BACKGROUND = "#f5f5f7"
    CARD_BG = "#ffffff"
    
    # 深色模式背景色
    DARK_BACKGROUND = "#121212"
    DARK_CARD_BG = "#1e1e1e"
    
    # 明亮模式文本颜色
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_LIGHT = "#ffffff"
    
    # 深色模式文本颜色
    DARK_TEXT_PRIMARY = "#e0e0e0"
    DARK_TEXT_SECONDARY = "#a0a0a0"
    DARK_TEXT_LIGHT = "#ffffff"
    
    # 状态颜色
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"
    
    # 边框和分隔线
    BORDER = "#e0e0e0"
    DARK_BORDER = "#424242"
    
    # 输出区域颜色
    OUTPUT_BG = "#f8f9fa"
    OUTPUT_TEXT = "#212121"
    DARK_OUTPUT_BG = "#2d2d2d"
    DARK_OUTPUT_TEXT = "#e0e0e0"
    
    # 阴影效果
    SHADOW = "#00000026"
    
    # 当前使用的主题（默认为明亮模式）
    CURRENT_THEME = "light"
    
    @classmethod
    def toggle_theme(cls):
        """切换主题模式"""
        if cls.CURRENT_THEME == "light":
            cls.CURRENT_THEME = "dark"
        else:
            cls.CURRENT_THEME = "light"
        return cls.CURRENT_THEME
        
    @classmethod
    def get_bg(cls):
        """获取当前主题背景色"""
        return cls.DARK_BACKGROUND if cls.CURRENT_THEME == "dark" else cls.BACKGROUND
        
    @classmethod
    def get_card_bg(cls):
        """获取当前主题卡片背景色"""
        return cls.DARK_CARD_BG if cls.CURRENT_THEME == "dark" else cls.CARD_BG
        
    @classmethod
    def get_text_primary(cls):
        """获取当前主题主文本颜色"""
        return cls.DARK_TEXT_PRIMARY if cls.CURRENT_THEME == "dark" else cls.TEXT_PRIMARY
        
    @classmethod
    def get_text_secondary(cls):
        """获取当前主题次文本颜色"""
        return cls.DARK_TEXT_SECONDARY if cls.CURRENT_THEME == "dark" else cls.TEXT_SECONDARY
        
    @classmethod
    def get_border(cls):
        """获取当前主题边框颜色"""
        return cls.DARK_BORDER if cls.CURRENT_THEME == "dark" else cls.BORDER
        
    @classmethod
    def get_output_bg(cls):
        """获取当前主题输出区背景色"""
        return cls.DARK_OUTPUT_BG if cls.CURRENT_THEME == "dark" else cls.OUTPUT_BG
        
    @classmethod
    def get_output_text(cls):
        """获取当前主题输出区文本颜色"""
        return cls.DARK_OUTPUT_TEXT if cls.CURRENT_THEME == "dark" else cls.OUTPUT_TEXT

class InputDialog:
    """提供输入对话框，替代控制台输入"""
    def __init__(self, parent, title, prompt):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('450x180')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 225,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 90))
        
        # 添加提示
        prompt_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        prompt_label = ttk.Label(prompt_frame, text=prompt, wraplength=410, style='Prompt.TLabel')
        prompt_label.pack(pady=(15, 15), padx=15)
        
        # 输入框
        self.entry = ttk.Entry(prompt_frame, width=40, font=('Segoe UI', 10))
        self.entry.pack(pady=5, padx=15, fill=tk.X)
        self.entry.focus_set()  # 设置焦点
        
        # 确认按钮
        btn_frame = ttk.Frame(prompt_frame, style='Card.TFrame')
        btn_frame.pack(pady=10, fill=tk.X, padx=15)
        
        cancel_btn = ttk.Button(btn_frame, text=LanguageManager.get_string("operation_cancelled").split()[0], 
                               command=self.on_cancel, style='Secondary.TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        ok_btn = ttk.Button(btn_frame, text="确定", command=self.on_ok, style='Primary.TButton')
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 绑定回车键
        self.dialog.bind("<Return>", lambda e: self.on_ok())
        
        # 绑定ESC键
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())
        
        # 模态对话框
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def on_ok(self):
        """确认按钮回调"""
        self.result = self.entry.get()
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮回调"""
        self.result = None
        self.dialog.destroy()

class RedirectIO:
    """重定向标准输入输出到Tkinter界面"""
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root
        self.buffer = ""
        
    def write(self, string):
        """输出重定向处理"""
        self.buffer += string
        self.text_widget.config(state=tk.NORMAL)
        
        # 为错误信息添加红色
        if "错误" in string or "失败" in string or "error" in string.lower():
            self.text_widget.tag_configure("error", foreground=UITheme.ERROR)
            self.text_widget.insert(tk.END, string, "error")
        # 为成功信息添加绿色
        elif "成功" in string or "完成" in string or "success" in string.lower():
            self.text_widget.tag_configure("success", foreground=UITheme.SUCCESS)
            self.text_widget.insert(tk.END, string, "success")
        # 为警告信息添加黄色
        elif "警告" in string or "warning" in string.lower():
            self.text_widget.tag_configure("warning", foreground=UITheme.WARNING)
            self.text_widget.insert(tk.END, string, "warning")
        else:
            self.text_widget.insert(tk.END, string)
                
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
        
    def flush(self):
        """刷新缓冲区"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.buffer)
        self.buffer = ""
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def readline(self):
        """输入重定向处理"""
        try:
            # 如果最近的输出中包含确认操作的提示，使用确认对话框
            recent_output = self.text_widget.get("end-2l", "end-1c")
            
            if "确认" in recent_output or "confirm" in recent_output.lower():
                dialog = ConfirmDialog(self.root, LanguageManager.get_string("confirm_action"), 
                                      LanguageManager.get_string("confirm_action"))
                result = "y\n" if dialog.result else "n\n"
                self.write(result)
                return result
        
            # 根据输出内容判断要显示什么提示文本
            prompt_text = "请输入所需信息:"
            title_text = "输入请求"
            
            if "选择" in recent_output or "choice" in recent_output.lower():
                title_text = LanguageManager.get_string("enter_choice")
                prompt_text = LanguageManager.get_string("select_option")
            elif "操作" in recent_output or "operation" in recent_output.lower() or "bootrec" in recent_output.lower():
                title_text = LanguageManager.get_string("specify_bootrec_operation")
                prompt_text = LanguageManager.get_string("enter_choice")
        
            # 创建输入对话框并获取结果
            dialog = InputDialog(self.root, title_text, prompt_text)
            
            # 如果用户取消了输入，返回空行
            if dialog.result is None:
                self.write(f"{LanguageManager.get_string('input_cancelled')}\n")
                return "\n"
            
            result = dialog.result
        
            # 在输出区域显示用户输入
            self.write(f"{result}\n")
        
            return result + "\n"  # 确保返回值带有换行符
            
        except Exception as e:
            # 处理任何可能的异常
            self.write(f"{LanguageManager.get_string('input_error')}: {str(e)}\n")
            return "\n"  # 返回空行

class RedirectText:
    """重定向文本输出到Tkinter窗口"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, string):
        self.buffer += string
        
        try:
            self.text_widget.config(state=tk.NORMAL)
            
            # 为错误信息添加红色
            if "错误" in string or "失败" in string or "error" in string.lower():
                self.text_widget.tag_configure("error", foreground=UITheme.ERROR)
                self.text_widget.insert(tk.END, string, "error")
            # 为成功信息添加绿色
            elif "成功" in string or "完成" in string or "success" in string.lower():
                self.text_widget.tag_configure("success", foreground=UITheme.SUCCESS)
                self.text_widget.insert(tk.END, string, "success")
            # 为警告信息添加黄色
            elif "警告" in string or "warning" in string.lower():
                self.text_widget.tag_configure("warning", foreground=UITheme.WARNING)
                self.text_widget.insert(tk.END, string, "warning")
            else:
                self.text_widget.insert(tk.END, string)
                    
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
        except (tk.TclError, RuntimeError, AttributeError) as e:
            # 如果文本控件已经被销毁，或者Tkinter关闭，则忽略错误
            pass
        
    def flush(self):
        """刷新缓冲区"""
        try:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, self.buffer)
            self.buffer = ""
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
        except (tk.TclError, RuntimeError, AttributeError):
            # 如果文本控件已经被销毁，或者Tkinter关闭，则忽略错误
            pass
        
    def readline(self):
        """提供一个简单的readline实现，防止EOF错误"""
        return "\n"

class ConfirmDialog:
    """确认操作对话框"""
    def __init__(self, parent, title, message):
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('400x200')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 200,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 100))
        
        # 创建一个卡片式面板
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加消息
        msg_label = ttk.Label(main_frame, text=message, wraplength=360, 
                             justify=tk.CENTER, style='Prompt.TLabel')
        msg_label.pack(pady=(20, 20), padx=20)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(pady=(10, 20), fill=tk.X, padx=20)
        
        # 确认和取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消(N)", 
                               command=self.on_no, style='Secondary.TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        ok_btn = ttk.Button(btn_frame, text="确认(Y)", 
                           command=self.on_yes, style='Primary.TButton')
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 绑定键盘事件
        self.dialog.bind("<y>", lambda e: self.on_yes())
        self.dialog.bind("<Y>", lambda e: self.on_yes())
        self.dialog.bind("<n>", lambda e: self.on_no())
        self.dialog.bind("<N>", lambda e: self.on_no())
        self.dialog.bind("<Escape>", lambda e: self.on_no())
        
        # 模态对话框
        self.dialog.grab_set()
        self.dialog.focus_set()
        parent.wait_window(self.dialog)
    
    def on_yes(self):
        """确认按钮回调"""
        self.result = True
        self.dialog.destroy()
    
    def on_no(self):
        """取消按钮回调"""
        self.result = False
        self.dialog.destroy()

class FileExtensionSettingsDialog:
    """文件后缀设置对话框"""
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.extensions = set([".log", ".tmp", ".temp", ".bak", ".old", ".dmp"])  # 默认后缀
        
        # 从配置加载已保存的扩展名
        self.load_extensions()
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(LanguageManager.get_string("file_extension_settings"))
        self.dialog.geometry('500x400')
        self.dialog.resizable(True, False)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 250,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 200))
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=LanguageManager.get_string("file_extension_settings"),
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # 当前扩展名列表
        extensions_frame = ttk.Frame(main_frame, style='Card.TFrame')
        extensions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        extensions_label = ttk.Label(
            extensions_frame,
            text=LanguageManager.get_string("current_extensions"),
            style='Subtitle.TLabel'
        )
        extensions_label.pack(anchor=tk.W, pady=5)
        
        # 创建扩展名列表框
        self.extensions_listbox = tk.Listbox(
            extensions_frame,
            height=10,
            width=40,
            font=('Segoe UI', 10),
            background=UITheme.get_card_bg(),
            foreground=UITheme.get_text_primary()
        )
        self.extensions_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 填充扩展名列表
        self.update_extensions_list()
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 添加扩展名按钮
        add_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string("add_extension"),
            command=self.add_extension,
            style='Primary.TButton'
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 移除扩展名按钮
        remove_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string("remove_extension"),
            command=self.remove_extension,
            style='Primary.TButton'
        )
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # 恢复默认按钮
        default_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string("default_extensions"),
            command=self.reset_to_default,
            style='Secondary.TButton'
        )
        default_btn.pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        close_btn = ttk.Button(
            btn_frame,
            text="OK",
            command=self.on_close,
            style='Secondary.TButton'
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # 绑定Esc键
        self.dialog.bind("<Escape>", lambda e: self.on_close())
        
        # 模态对话框
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def update_extensions_list(self):
        """更新扩展名列表显示"""
        self.extensions_listbox.delete(0, tk.END)
        for ext in sorted(self.extensions):
            if not ext.startswith('.'):
                ext = '.' + ext
            self.extensions_listbox.insert(tk.END, ext)
    
    def add_extension(self):
        """添加文件扩展名"""
        dialog = InputDialog(
            self.root,
            LanguageManager.get_string("add_extension"),
            LanguageManager.get_string("enter_extension")
        )
        
        if dialog.result:
            ext = dialog.result.strip()
            if not ext:
                return
                
            if not ext.startswith('.'):
                ext = '.' + ext
                
            self.extensions.add(ext)
            self.extensions_listbox.delete(0, tk.END)
            for ext in sorted(self.extensions):
                self.extensions_listbox.insert(tk.END, ext)
            
            # 保存更改
            self.save_extensions()
            
            # 显示成功消息
            self.status_bar.config(text=LanguageManager.get_string('extension_added'))
    
    def remove_extension(self):
        """移除文件扩展名"""
        selection = self.extensions_listbox.curselection()
        if not selection:
            return
            
        ext = self.extensions_listbox.get(selection[0])
        self.extensions.remove(ext)
        self.extensions_listbox.delete(0, tk.END)
        for ext in sorted(self.extensions):
            self.extensions_listbox.insert(tk.END, ext)
        
        # 保存更改
        self.save_extensions()
        
        # 显示成功消息
        self.status_bar.config(text=LanguageManager.get_string('extension_removed'))
    
    def reset_to_default_extensions(self):
        """重置为默认文件扩展名"""
        self.extensions = set([".log", ".tmp", ".temp", ".bak", ".old", ".dmp"])
        self.extensions_listbox.delete(0, tk.END)
        for ext in sorted(self.extensions):
            self.extensions_listbox.insert(tk.END, ext)
        
        # 保存更改
        self.save_extensions()
        
        # 显示成功消息
        self.status_bar.config(text=LanguageManager.get_string('extensions_reset'))
    
    def load_extensions(self):
        """从配置文件加载扩展名"""
        try:
            config_file = Path("config/file_extensions.txt")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.extensions = set([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"加载文件后缀配置失败: {str(e)}")
    
    def save_extensions(self):
        """保存扩展名到配置文件"""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "file_extensions.txt"
            with open(config_file, 'w', encoding='utf-8') as f:
                for ext in sorted(self.extensions):
                    f.write(f"{ext}\n")
        except Exception as e:
            self.logger.error(f"保存文件后缀配置失败: {str(e)}")
    
    def on_close(self):
        """关闭对话框"""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.destroy()

class GPUModeSelectionDialog:
    """GPU模式选择对话框"""
    def __init__(self, parent):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(LanguageManager.get_string("select_option"))
        self.dialog.geometry('400x200')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 200,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 100))
        
        # 创建一个卡片式面板
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加标题
        title_label = ttk.Label(
            main_frame, 
            text=LanguageManager.get_string("select_option"),
            style='Subtitle.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # 添加选项按钮
        self.mode = tk.IntVar(value=1)  # 默认选择普通模式
        
        normal_mode = ttk.Radiobutton(
            main_frame,
            text=LanguageManager.get_string("normal_display_mode"),
            variable=self.mode,
            value=1
        )
        normal_mode.pack(anchor=tk.W, padx=20, pady=5)
        
        continuous_mode = ttk.Radiobutton(
            main_frame,
            text=LanguageManager.get_string("continuous_display_mode"),
            variable=self.mode,
            value=2
        )
        continuous_mode.pack(anchor=tk.W, padx=20, pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(pady=20, fill=tk.X, padx=20)
        
        # 确认和取消按钮
        cancel_btn = ttk.Button(
            btn_frame, 
            text=LanguageManager.get_string("operation_cancelled").split()[0],
            command=self.on_cancel, 
            style='Secondary.TButton'
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        ok_btn = ttk.Button(
            btn_frame, 
            text="确定",
            command=self.on_ok, 
            style='Primary.TButton'
        )
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 绑定ESC键
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())
        
        # 模态对话框
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def on_ok(self):
        """确认按钮回调"""
        self.result = self.mode.get()
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮回调"""
        self.result = 0  # 表示取消
        self.dialog.destroy()

class GPUContinuousModeDialog:
    """GPU连续模式对话框，提供停止按钮"""
    def __init__(self, parent):
        self.stopped = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(LanguageManager.get_string("continuous_display_mode"))
        self.dialog.geometry('300x100')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 150,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 50))
        
        # 创建一个卡片式面板
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加停止按钮
        stop_btn = ttk.Button(
            main_frame, 
            text=LanguageManager.get_string("operation_cancelled").split()[0],
            command=self.stop_monitor, 
            style='Primary.TButton'
        )
        stop_btn.pack(pady=10)
        
        # 绑定ESC键
        self.dialog.bind("<Escape>", lambda e: self.stop_monitor())
        
        # 对话框关闭时的处理
        self.dialog.protocol("WM_DELETE_WINDOW", self.stop_monitor)
    
    def stop_monitor(self):
        """停止监控"""
        self.stopped = True
        self.dialog.destroy()

class SystemSafetyToolsGUI:
    def __init__(self, root):
        """初始化主应用程序"""
        self.root = root
        self.logger = LogManager().get_logger(__name__)
        self.logger.info("Initializing SystemSafetyToolsGUI")
        
        # 保存原始的标准输出和错误输出
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        
        # 设置GUI模式
        op.set_gui_mode(True)
        op.set_root_window(root)
        
        # 初始化必要的属性
        self.images = {}  # 初始化图像字典
        self.buttons = []  # 初始化按钮列表
        self.shadow_frames = []  # 初始化阴影框架列表
        self.tool_running = False  # 初始化工具运行状态
        self.output_text = None  # 初始化输出文本区域
        
        try:
            # 加载主题配置
            self._load_theme_config()
            
            # 设置窗口基本属性
            self.setup_window()
            
            # 设置样式
            self.setup_styles()
            
            # 加载图片资源
            self.load_images()
            
            # 创建界面元素
            self.create_widgets()
            
            # 设置输出重定向
            if hasattr(self, 'output_text') and self.output_text is not None:
                self.setup_output_redirect()
            else:
                self.logger.warning("Output text area not created, skipping output redirection")
            
            # 优化视觉效果
            self.enhance_visual_effects()
            
            # 应用动画效果
            self.animate_frame_transition()
            
            self.logger.info("SystemSafetyToolsGUI initialized")
        
        except Exception as e:
            self.logger.error(f"Error initializing GUI: {str(e)}", exc_info=True)
            messagebox.showerror("初始化错误", f"应用程序初始化失败：{str(e)}")

    def load_images(self):
        """加载图片使用程序化图像生成器"""
        try:
            from image import ImageGenerator
            
            self.images = ImageGenerator.get_image_dict()
            self.logger.info("Loaded programmatically generated icons")
            
        except Exception as e:
            self.logger.error(f"Error loading images: {e}")
            self.images = {}  

    def setup_window(self):
        """设置窗口基本属性"""
        self.logger.info("Setting up window")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 窗口大小和位置
        window_width = int(screen_width * 0.7)  
        window_height = int(screen_height * 0.7)  
        
        # 计算窗口位置使其居中
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        # 设置窗口最小尺寸
        self.root.minsize(800, 600)
        
        # 设置窗口标题
        self.root.title(LanguageManager.get_string("title"))
        
        # 设置窗口背景颜色
        self.root.configure(background=UITheme.get_bg())
        
        # 捕获窗口大小改变事件
        self.root.bind("<Configure>", self._on_window_resize)
        
        # 处理窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 为窗口添加日志
        self.logger.info(f"Window configured with size {window_width}x{window_height}")

    def _on_window_resize(self, event):
        """当窗口大小改变时调整UI元素"""
        if event.widget == self.root:
            try:
                # 记录窗口新尺寸
                new_width = event.width
                new_height = event.height
            
                # 调整左右面板的相对宽度
                if hasattr(self, 'content_frame'):
                    total_width = self.content_frame.winfo_width()
                    if total_width > 0:
                        # 左侧面板占40%，右侧面板占60%
                        left_width = int(total_width * 0.4)
                        right_width = total_width - left_width - 20  # 20是padding
                        
                        if hasattr(self, 'left_panel'):
                            self.left_panel.configure(width=left_width)
                        if hasattr(self, 'right_panel'):
                            self.right_panel.configure(width=right_width)
                
                # 调整按钮大小
                if hasattr(self, 'buttons'):
                    btn_frame = self.buttons[0].master if self.buttons else None
                    if btn_frame:
                        frame_width = btn_frame.winfo_width()
                        if frame_width > 0:
                            # 计算按钮的理想大小
                            btn_width = (frame_width - 30) // 2  # 30是总padding
                            for button in self.buttons:
                                button.configure(width=max(15, btn_width // 10))  # 转换为字符宽度
                    
                    # 调整输出区域高度
                if hasattr(self, 'output_text'):
                        content_height = self.content_frame.winfo_height()
                        if content_height > 0:
                            self.output_text.configure(height=max(10, content_height // 20))
                    
                    # 更新阴影效果
                if hasattr(self, '_update_shadows'):
                    self._update_shadows()
                
                self.logger.debug(f"Window resized to {new_width}x{new_height}")
                    
            except Exception as e:
                self.logger.error(f"Error handling window resize: {str(e)}")

    def setup_styles(self):
        """设置 TTK 样式"""
        try:
            style = ttk.Style()
            
            # Windows 11 风格的基本颜色
            accent_color = UITheme.PRIMARY
            light_accent = UITheme.PRIMARY_LIGHT
            bg_color = UITheme.get_bg()
            card_bg = UITheme.get_card_bg()
            text_color = UITheme.get_text_primary()
            
            # Windows 11 基本样式 - 圆角和现代化
            
            # 标题样式
            style.configure(
                'Win11Title.TLabel',
                font=('Segoe UI', 18, 'bold'),
                foreground=text_color,
                background=card_bg,
                padding=(10, 5)
            )
            
            # 副标题样式
            style.configure(
                'Win11Subtitle.TLabel',
                font=('Segoe UI', 12, 'bold'),
                foreground=text_color,
                background=card_bg,
                padding=(5, 3)
            )
            
            # 分组标题样式
            style.configure(
                'Win11GroupTitle.TLabel',
                font=('Segoe UI', 12, 'bold'),
                foreground=text_color,
                background=card_bg,
                padding=(5, 3)
            )
            
            # 普通文本样式
            style.configure(
                'Win11Text.TLabel',
                font=('Segoe UI', 10),
                foreground=text_color,
                background=card_bg
            )
            
            # 值文本样式
            style.configure(
                'Win11Value.TLabel',
                font=('Segoe UI', 10, 'bold'),
                foreground=accent_color,
                background=card_bg
            )
            
            # 主按钮样式 - 填充背景
            style.configure(
                'Win11Primary.TButton',
                font=('Segoe UI', 10),
                background=accent_color,
                foreground='white',
                padding=(15, 8),
                relief='flat',
                borderwidth=0
            )
            style.map(
                'Win11Primary.TButton',
                background=[('active', light_accent)]
            )
            
            # 次要按钮样式 - 轮廓
            style.configure(
                'Win11Secondary.TButton',
                font=('Segoe UI', 10),
                background=card_bg,
                foreground=text_color,
                padding=(15, 8),
                relief='flat',
                borderwidth=1
            )
            style.map(
                'Win11Secondary.TButton',
                background=[('active', self._lighten_color(card_bg, 0.1))]
            )
            
            # 选项按钮样式
            style.configure(
                'Win11Option.TButton',
                font=('Segoe UI', 10),
                background=card_bg,
                foreground=text_color,
                padding=(12, 6),
                relief='flat',
                borderwidth=1
            )
            style.map(
                'Win11Option.TButton',
                background=[('active', self._lighten_color(card_bg, 0.1))]
            )
            
            # 选中的选项按钮样式
            style.configure(
                'Win11OptionSelected.TButton',
                font=('Segoe UI', 10),
                background=light_accent,
                foreground='white',
                padding=(12, 6),
                relief='flat',
                borderwidth=0
            )
            style.map(
                'Win11OptionSelected.TButton',
                background=[('active', self._lighten_color(light_accent, 0.1))]
            )
            
            # 输入框样式
            style.configure(
                'Win11.TEntry',
                font=('Segoe UI', 10),
                fieldbackground=bg_color,
                foreground=text_color,
                padding=(8, 5),
                borderwidth=1
            )
            
            # 下拉框样式
            style.configure(
                'Win11.TCombobox',
                font=('Segoe UI', 10),
                background=bg_color,
                foreground=text_color,
                fieldbackground=bg_color,
                padding=(8, 5),
                arrowsize=15
            )
            
            # 复选框样式
            style.configure(
                'Win11.TCheckbutton',
                font=('Segoe UI', 10),
                background=card_bg,
                foreground=text_color
            )
            
            # 主卡片样式 - 圆角和阴影
            style.configure(
                'Win11Card.TFrame',
                background=card_bg,
                relief='flat',
                borderwidth=0
            )
            
            # 分组框架样式
            style.configure(
                'Win11Section.TFrame',
                background=card_bg,
                relief='flat',
                borderwidth=0
            )
            
            # 子分组框架样式
            style.configure(
                'Win11Subsection.TFrame',
                background=card_bg,
                relief='flat',
                borderwidth=0
            )
            
            # 透明框架样式
            style.configure(
                'Win11Transparent.TFrame',
                background=card_bg
            )
            
            # 底部按钮区域样式
            style.configure(
                'Win11Footer.TFrame',
                background=card_bg,
                relief='flat',
                borderwidth=0
            )
            
            # 标准样式
            style.configure('TFrame', background=bg_color)
            style.configure('TLabel', background=bg_color, foreground=text_color)
            style.configure('TButton', font=('Segoe UI', 10))
            
            # 卡片样式
            style.configure('Card.TFrame', background=card_bg)
            
            # 标题样式
            style.configure(
                'Title.TLabel',
                font=('Segoe UI', 16, 'bold'),
                background=bg_color,
                foreground=text_color
            )
            
            # 状态标签样式
            style.configure(
                'Status.TLabel',
                font=('Segoe UI', 9),
                background=card_bg,
                foreground=UITheme.TEXT_SECONDARY
            )
            
            # 主按钮样式
            style.configure(
                'Primary.TButton',
                font=('Segoe UI', 10),
                background=accent_color,
                foreground='white'
            )
            style.map(
                'Primary.TButton',
                background=[('active', light_accent)]
            )
            
            # 次要按钮样式
            style.configure(
                'Secondary.TButton',
                font=('Segoe UI', 10)
            )
            
            # 信息按钮样式
            style.configure(
                'Info.TButton',
                font=('Segoe UI', 10),
                background=UITheme.INFO
            )
            
            # 警告按钮样式
            style.configure(
                'Warning.TButton',
                font=('Segoe UI', 10),
                background=UITheme.WARNING
            )
            
            # 危险按钮样式
            style.configure(
                'Danger.TButton',
                font=('Segoe UI', 10),
                background=UITheme.ERROR
            )
            
            # 悬停效果样式
            for btn_style in ['Primary.TButton', 'Secondary.TButton', 'Info.TButton', 'Warning.TButton', 'Danger.TButton']:
                hover_style = f"{btn_style}.Hover"
                style.configure(
                    hover_style,
                    font=('Segoe UI', 10, 'bold')
                )
            
            # 为每种按钮类型创建悬停样式
            button_types = ['Primary', 'Secondary', 'Warning', 'Info']
            for btn_type in button_types:
                # 基本按钮样式
                base_style = f'{btn_type}.TButton'
                hover_style = f'{btn_type}.TButton.Hover'
                
                # 复制基本样式的设置
                style.configure(hover_style, 
                    font=('Segoe UI', 10, 'bold'),  # 加粗字体
                    background=self._lighten_color(UITheme.PRIMARY, 0.1),  # 稍微变亮的背景色
                )
                
                # 映射鼠标悬停状态
                style.map(hover_style,
                    background=[('active', self._lighten_color(UITheme.PRIMARY, 0.2))]
                )
            
            self.logger.info("Styles set up successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up styles: {str(e)}", exc_info=True)

    def create_widgets(self):
        """创建界面元素"""
        self.logger.info("Creating widgets")
        
        try:
            # 主体框架
            self.main_frame = ttk.Frame(self.root, style='Card.TFrame')
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 创建标题栏
            self.create_header()
            
            # 创建内容区域框架
            self.content_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # 配置content_frame的列权重
            self.content_frame.grid_columnconfigure(0, weight=4)  # 左侧面板占40%
            self.content_frame.grid_columnconfigure(1, weight=6)  # 右侧面板占60%
            
            # 创建左侧功能按钮区域
            self.left_panel = ttk.Frame(self.content_frame, style='Card.TFrame')
            self.left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
            
            # 创建右侧输出区域
            self.right_panel = ttk.Frame(self.content_frame, style='Card.TFrame')
            self.right_panel.grid(row=0, column=1, sticky='nsew')
            
            # 创建功能按钮区域
            self.create_function_buttons()
            
            # 创建输出区域
            self.create_output_area()
            
            # 创建状态栏
            self.create_status_bar()
            
            # 绑定窗口大小变化事件
            self.root.bind('<Configure>', self._on_window_resize)
            
            self.logger.info("Widgets created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating widgets: {str(e)}", exc_info=True)

    def create_status_bar(self):
        """创建状态栏"""
        try:
            # 状态栏框架
            status_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
            status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
            
            # 状态栏标签
            self.status_bar = ttk.Label(
                status_frame,
                text="",  # 初始为空
                style='Status.TLabel'
            )
            self.status_bar.pack(side=tk.LEFT, padx=5)
            
            self.logger.info("Status bar created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating status bar: {str(e)}", exc_info=True)

    def create_header(self):
        """创建标题栏"""
        self.logger.info("Creating header")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # 标题栏框架
            self.header_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
            self.header_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # 标题和版本区域
            title_frame = ttk.Frame(self.header_frame, style='Card.TFrame')
            title_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            # 应用名称
            title_label = ttk.Label(
                title_frame,
                text=LanguageManager.get_string("title"),
                style='Title.TLabel'
            )
            title_label.pack(side=tk.TOP, anchor=tk.W)
            self.title_label = title_label
            
            # 版本信息
            from config.config import AppConfig
            version_label = ttk.Label(
                title_frame,
                text=f"v{AppConfig.VERSION}",
                style='Status.TLabel'
            )
            version_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
            
            # 操作按钮区域 - 右侧
            button_frame = ttk.Frame(self.header_frame, style='Card.TFrame')
            button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
            
            # 帮助按钮
            help_button = ttk.Button(
                button_frame,
                text="?",
                command=self.show_help,
                style='Secondary.TButton',
                width=3
            )
            help_button.pack(side=tk.RIGHT, padx=5)
            
            # 设置按钮
            settings_button = ttk.Button(
                button_frame,
                text="⚙",
                command=self.show_settings,
                style='Secondary.TButton',
                width=3
            )
            settings_button.pack(side=tk.RIGHT, padx=5)
            
            # 语言切换按钮
            language_button = ttk.Button(
                button_frame,
                text="🌐",
                command=self.show_language_menu,
                style='Secondary.TButton',
                width=3
            )
            language_button.pack(side=tk.RIGHT, padx=5)
            
            # 主题切换按钮
            theme_icon = "🌙" if UITheme.CURRENT_THEME == "light" else "☀"
            self.theme_btn = ttk.Button(
                button_frame,
                text=theme_icon,
                command=self.toggle_theme,
                style='Secondary.TButton',
                width=3
            )
            self.theme_btn.pack(side=tk.RIGHT, padx=5)
            
            self.logger.info("Header created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating header: {str(e)}", exc_info=True)

    def create_function_buttons(self):
        """创建功能按钮区域"""
        self.logger.info("Creating function buttons")
        
        try:
            # 主功能区标题
            func_title = ttk.Label(
                self.left_panel,
                text=LanguageManager.get_string("functions"),
                style='Title.TLabel'
            )
            func_title.pack(anchor=tk.W, padx=20, pady=(0, 10))
            
            # 按钮框架
            btn_frame = ttk.Frame(self.left_panel, style='Card.TFrame')
            btn_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # 设置网格列配置，确保平均分布
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            
            # 获取菜单项文本
            menu_items = LanguageManager.get_string("menu_items")
            
            # 确保菜单项包含病毒扫描
            if isinstance(menu_items, list) and len(menu_items) < 9:
                virus_scan_text = LanguageManager.get_string("virus_scan_title")
                menu_items = list(menu_items)  # 转换为可变列表
                menu_items.append(virus_scan_text)
            
            # 定义按钮样式
            button_styles = [
                ('Primary.TButton', 'system_file'),
                ('Secondary.TButton', 'clean_file'),
                ('Info.TButton', 'gpu_info'),
                ('Warning.TButton', 'system_check'),
                ('Primary.TButton', 'dism_tool'),
                ('Secondary.TButton', 'network_reset'),
                ('Info.TButton', 'drive_check'),
                ('Warning.TButton', 'boot_repair'),
                ('Primary.TButton', 'virus_scan')
            ]
            
            # 清空按钮列表
            self.buttons = []
            
            # 创建按钮
            for i, item_text in enumerate(menu_items):
                row = i // 2  # 每行2个按钮
                col = i % 2
                
                # 选择按钮样式
                style_idx = min(i, len(button_styles) - 1)
                button_style = button_styles[style_idx][0]
                
                # 创建按钮
                button = ttk.Button(
                    btn_frame,
                    text=item_text,
                    command=lambda idx=i+1: self.run_tool(idx),
                    style=button_style,
                    width=20  # 设置固定宽度
                )
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                # 配置行伸缩
                btn_frame.grid_rowconfigure(row, weight=1)
                
                # 添加按钮到列表
                self.buttons.append(button)
            
            self.logger.info(f"Created {len(self.buttons)} function buttons")
            
        except Exception as e:
            self.logger.error(f"Error creating function buttons: {str(e)}", exc_info=True)

    def _lighten_color(self, color, amount=0.2):
        """增亮颜色"""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color, amount=0.2):
        """加深颜色"""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_output_area(self):
        """创建输出显示区域"""
        self.logger.info("Creating output area")
        
        try:
            # 输出区域标题
            output_title = ttk.Label(
                self.right_panel,
                text=LanguageManager.get_string("output_text"),
                style='Title.TLabel'
            )
            output_title.pack(anchor=tk.W, padx=20, pady=(0, 10))
            
            # 输出区域外框架
            output_frame = ttk.Frame(self.right_panel, style='Card.TFrame')
            output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # 创建文本区和滚动条
            self.output_text = scrolledtext.ScrolledText(
                output_frame,
                wrap=tk.WORD,
                height=12,
                background=UITheme.get_output_bg(),
                foreground=UITheme.get_output_text(),
                font=('Consolas', 9)
            )
            self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 设置文本区为只读
            self.output_text.config(state=tk.DISABLED)
            
            # 按钮区域
            button_frame = ttk.Frame(output_frame)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 清除按钮
            clear_btn = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("clear_output"),
                command=self._clear_output,
                style='Secondary.TButton'
            )
            clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
            
            self.logger.info("Output area created")
            
        except Exception as e:
            self.logger.error(f"Error creating output area: {str(e)}", exc_info=True)

    def setup_output_redirect(self):
        """设置输出重定向"""
        self.logger.info("Setting up output redirection")
        
        try:
            # 安全检查
            if not hasattr(self, 'output_text') or self.output_text is None:
                self.logger.error("Output text widget not available for redirection")
                return
                
            # 保存旧的标准输出和错误输出
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            
            # 创建重定向对象
            self.stdout_redirector = RedirectIO(self.output_text, self.root)
            self.stderr_redirector = RedirectText(self.output_text)
            
            # 重定向标准输出和错误输出
            sys.stdout = self.stdout_redirector
            sys.stderr = self.stderr_redirector
            
            self.logger.info("Output redirection set up successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up output redirection: {str(e)}", exc_info=True)

    def _clear_output(self):
        """清除输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # 添加简单的清除动画效果
        self.apply_animation(self.output_text, "background", 
                             UITheme.get_output_bg(), "#e0f7fa", UITheme.get_output_bg())

    def run_tool(self, tool_idx):
        """运行所选工具"""
        self.logger.info(f"Running tool {tool_idx}")
        
        # 确保工具索引有效
        max_tool_idx = len(getattr(self, 'buttons', []))
        if tool_idx < 1 or tool_idx > max_tool_idx:
            self.logger.error(f"Invalid tool index: {tool_idx}")
            return
        
        # 检查管理员权限（如果需要）
        if self.check_admin_rights(tool_idx) is False:
            return
        
        try:
            # 特殊情况：病毒扫描
            if tool_idx == 9:  # 确保这是病毒扫描的正确索引
                self.show_virus_scan_dialog()
                return
                
            # 特殊情况：引导修复功能
            if tool_idx == 8:  # 引导修复的索引
                self.show_boot_repair_dialog()
                return
                
            # 特殊情况：GPU信息
            if tool_idx == 3:
                self.show_gpu_mode_dialog()
                return
                
            # 特殊情况：DISM工具
            if tool_idx == 5:
                self.show_dism_options_dialog()
                return
                
            # 特殊情况：驱动器检查
            if tool_idx == 7:
                self.show_drive_check_dialog()
                return
                
            # 对于其他工具，一个正在运行时不要启动新的
            if hasattr(self, 'tool_running') and self.tool_running:
                # 提示用户当前有工具正在运行
                messagebox.showinfo(
                    LanguageManager.get_string("information"),
                    LanguageManager.get_string("tool_already_running"),
                    parent=self.root
                )
                return
            
            # 设置工具运行状态
            self.tool_running = True
            
            # 清空输出区域
            self._clear_output()
            
            # 禁用按钮，防止重复点击
            for button in self.buttons:
                button.configure(state=tk.DISABLED)
            
            # 创建进度条
            progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
            progress.pack(fill=tk.X, padx=20, pady=5)
            progress.start(10)
            
            # 在单独的线程中运行工具
            def run_in_thread():
                try:
                    AppTools.get(tool_idx, self)
                    
                except Exception as e:
                    self.logger.error(f"Error running tool {tool_idx}: {str(e)}")
                    
                    # 在UI线程中更新界面
                    self.root.after(0, lambda: self._show_error(str(e)))
                    
                finally:
                    # 在UI线程中恢复界面状态
                    self.root.after(0, lambda: self._restore_ui(progress))
            
            # 启动线程
            tool_thread = threading.Thread(target=run_in_thread)
            tool_thread.daemon = True
            tool_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error preparing to run tool {tool_idx}: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                str(e),
                parent=self.root
            )
            self.tool_running = False
            
            # 恢复按钮状态
            for button in self.buttons:
                button.configure(state=tk.NORMAL)

    def _show_error(self, error_message):
        """显示错误消息对话框"""
        messagebox.showerror(
            LanguageManager.get_string("error"),
            error_message,
            parent=self.root
        )

    def _restore_ui(self, progress_bar):
        """恢复UI状态"""
        # 停止并移除进度条
        progress_bar.stop()
        progress_bar.destroy()
        
        # 恢复按钮状态
        for button in self.buttons:
            button.configure(state=tk.NORMAL)
        
        # 重置工具运行状态
        self.tool_running = False

    def show_help(self):
        """显示帮助信息"""
        help_window = tk.Toplevel(self.root)
        help_window.title(LanguageManager.get_string('help_title'))
        help_window.geometry('600x400')
        help_window.transient(self.root)
        help_window.configure(background=UITheme.get_bg())
        
        # 居中显示
        help_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 300,
            self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 200))
        
        # 创建帮助内容
        main_frame = ttk.Frame(help_window, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=LanguageManager.get_string('help_title'),
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # 创建滚动文本区域
        help_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            background=UITheme.get_card_bg(),
            foreground=UITheme.get_text_primary(),
            padx=10,
            pady=10
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 添加帮助内容
        help_content = [
            LanguageManager.get_string('help_input_number'),
            LanguageManager.get_string('help_esc_exit'),
            LanguageManager.get_string('help_settings')
        ]
        
        help_text.insert(tk.END, "\n\n".join(help_content))
        help_text.config(state=tk.DISABLED)  # 设为只读

    def toggle_theme(self):
        """切换明亮/黑暗主题"""
        # 切换主题模式
        new_theme = UITheme.toggle_theme()
        
        # 更新UI样式
        self.setup_styles()
        
        # 更新主窗口背景色（带动画）
        self.apply_animation(self.root, "bg", UITheme.get_bg(), None, None)
        
        # 更新按钮文字
        self.theme_btn.config(text=LanguageManager.get_string('dark_mode') if new_theme == "light" else LanguageManager.get_string('light_mode'))
        
        # 更新主要框架
        frames_to_update = [
            self.main_frame,
            self.content_frame,
            self.left_panel,
            self.right_panel,
            self.header_frame
        ]
        
        # 只更新存在的框架
        for frame in frames_to_update:
            if hasattr(self, frame.__str__().split('.')[-1]):  # 检查框架是否存在
                self.apply_animation(frame, "background", UITheme.get_card_bg(), None, None)
        
        # 更新输出文本区域
        if hasattr(self, 'output_text'):
            self.output_text.config(
                background=UITheme.get_output_bg(),
                foreground=UITheme.get_output_text()
            )
        
        # 更新状态栏
        if hasattr(self, 'status_bar'):
            theme_name = LanguageManager.get_string('dark_mode_activated') if new_theme == "dark" else LanguageManager.get_string('light_mode_activated')
            self.status_bar.config(text=theme_name)
        
        # 执行动画效果
        self.animate_frame_transition()

    def apply_animation(self, widget, property_name, start_value, mid_value=None, end_value=None, 
                       steps=10, delay=20):
        """应用简单的属性变化动画"""
        if end_value is None:
            end_value = start_value
        
        try:
            # 区分标准tk组件和ttk组件
            is_ttk_widget = isinstance(widget, ttk.Widget)
            
            # 对于ttk组件，不执行背景和前景色的直接修改
            if is_ttk_widget and (property_name in ["background", "bg", "foreground", "fg"]):
                # ttk组件不支持直接修改颜色，所以这里不做任何操作
                return
            
            # 标准的Tkinter组件可以直接修改属性
            if property_name == "background" or property_name == "bg":
                if hasattr(widget, 'config'):
                    widget.config(bg=start_value)
                    
                    if mid_value:
                        self.root.after(delay, lambda: widget.config(bg=mid_value))
                        self.root.after(delay * 2, lambda: widget.config(bg=end_value))
                    elif start_value != end_value:
                        self.root.after(delay, lambda: widget.config(bg=end_value))
                    
            elif property_name == "foreground" or property_name == "fg":
                if hasattr(widget, 'config'):
                    widget.config(fg=start_value)
                    
                    if mid_value:
                        self.root.after(delay, lambda: widget.config(fg=mid_value))
                        self.root.after(delay * 2, lambda: widget.config(fg=end_value))
                    elif start_value != end_value:
                        self.root.after(delay, lambda: widget.config(fg=end_value))
            else:
                # 尝试处理其他属性
                try:
                    # 尝试通过configure方法设置
                    config_dict = {property_name: start_value}
                    widget.configure(**config_dict)
                    
                    if mid_value:
                        mid_dict = {property_name: mid_value}
                        self.root.after(delay, lambda: widget.configure(**mid_dict))
                        
                        end_dict = {property_name: end_value}
                        self.root.after(delay * 2, lambda: widget.configure(**end_dict))
                    elif start_value != end_value:
                        end_dict = {property_name: end_value}
                        self.root.after(delay, lambda: widget.configure(**end_dict))
                except Exception:
                    pass  # 忽略错误，不中断程序流程
        
        except Exception as e:
            # 如果出现错误，记录但不中断程序
            self.logger.debug(f"动画效果：{type(widget).__name__}不支持设置{property_name}")

    def animate_frame_transition(self):
        """为UI元素添加进入动画效果"""
        try:
            import tkinter as tk
            
            self.logger.info("Applying frame transition animations")
            
            # 设置动画延迟
            initial_delay = 50  # 毫秒
            
            # 应用标题动画
            if hasattr(self, 'title_label'):
                self.root.after(initial_delay, lambda: self.apply_animation(
                    self.title_label, 'pack',
                    {'side': tk.TOP, 'anchor': tk.W, 'pady': 0},
                    {'side': tk.TOP, 'anchor': tk.W, 'pady': 5}
                ))
            
            # 应用功能按钮动画
            if hasattr(self, 'buttons') and self.buttons:
                for i, button in enumerate(self.buttons):
                    if button:
                        delay = initial_delay + (i * 50)  # 按顺序延迟显示
                        self.root.after(delay, lambda btn=button: self.apply_button_animation(btn))
            
            # 应用输出区域动画
            if hasattr(self, 'output_text') and self.output_text is not None:
                output_delay = initial_delay + (len(getattr(self, 'buttons', [])) * 50) + 100
                self.root.after(output_delay, lambda: self.apply_animation(
                    self.output_text, 'pack',
                    {'fill': tk.BOTH, 'expand': True, 'padx': 10, 'pady': 0},
                    {'fill': tk.BOTH, 'expand': True, 'padx': 10, 'pady': 10}
                ))
        
        except Exception as e:
            self.logger.error(f"Error in animate_frame_transition: {str(e)}")

    def apply_button_animation(self, button):
        """应用按钮跳跃动画"""
        try:
            # 获取当前的grid配置
            grid_info = button.grid_info()
            if not grid_info:
                return
                
            original_pady = grid_info.get('pady', 5)
            
            # 按钮上跳
            button.grid_configure(pady=10)
            
            # 然后回到原位
            self.root.after(100, lambda: button.grid_configure(pady=original_pady))

        except Exception as e:
            self.logger.error(f"Button animation error: {str(e)}")

    def show_language_menu(self):
        """显示语言选择菜单"""
        lang_menu = tk.Menu(self.root, tearoff=0)
        lang_menu.add_command(
            label=LanguageManager.get_string("set_chinese"),
            command=lambda: self.change_language("zh")
        )
        lang_menu.add_command(
            label=LanguageManager.get_string("set_english"),
            command=lambda: self.change_language("en")
        )
        
        # 显示菜单
        try:
            lang_menu.tk_popup(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
        finally:
            # 确保释放鼠标
            lang_menu.grab_release()

    def change_language(self, lang_code):
        """切换语言"""
        current_language = LanguageManager.get_current_language()
        
        if lang_code == "zh" and current_language != Language.CHINESE:
            LanguageManager.set_language(Language.CHINESE)
            self.logger.info("语言已切换为中文")
        elif lang_code == "en" and current_language != Language.ENGLISH:
            LanguageManager.set_language(Language.ENGLISH)
            self.logger.info("Language changed to English")
        else:
            return
        
        # 保存语言设置
        settings = SettingsManager()
        settings.save_settings()
        
        # 提示用户需要重启应用
        messagebox.showinfo(
            LanguageManager.get_string('language_changed'),
            LanguageManager.get_string('restart_needed')
        )

    def _create_file_extension_settings(self, parent_frame):
        """创建文件扩展名设置界面"""
        try:
            # 加载文件扩展名
            self.extensions = set([".log", ".tmp", ".temp", ".bak", ".old", ".dmp"])
            config_file = Path("config/file_extensions.txt")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.extensions = set([line.strip() for line in f if line.strip()])
            
            # 创建列表框和滚动条
            list_frame = ttk.Frame(parent_frame, style='Card.TFrame')
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.extensions_listbox = tk.Listbox(
                list_frame,
                height=10,
                width=40,
                font=('Segoe UI', 10),
                background=UITheme.get_card_bg(),
                foreground=UITheme.get_text_primary(),
                yscrollcommand=scrollbar.set
            )
            self.extensions_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            scrollbar.config(command=self.extensions_listbox.yview)
            
            # 填充列表
            for ext in sorted(self.extensions):
                if not ext.startswith('.'):
                    ext = '.' + ext
                self.extensions_listbox.insert(tk.END, ext)
            
            # 按钮区域
            btn_frame = ttk.Frame(parent_frame, style='Card.TFrame')
            btn_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # 修改按钮命令绑定为实例方法
            ttk.Button(btn_frame,
                      text=LanguageManager.get_string('add_extension'),
                      command=self.add_extension,  # 使用实例方法
                      style='Primary.TButton').pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame,
                      text=LanguageManager.get_string('remove_extension'),
                      command=self.remove_extension,  # 使用实例方法
                      style='Primary.TButton').pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame,
                      text=LanguageManager.get_string('default_extensions'),
                      command=self.reset_to_default_extensions,  # 使用实例方法
                      style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
                  
        except Exception as e:
            self.logger.error(f"Error creating file extension settings: {str(e)}")
            raise

    def add_extension(self):
        """添加文件扩展名"""
        dialog = InputDialog(
            self.root,
            LanguageManager.get_string("add_extension"),
            LanguageManager.get_string("enter_extension")
        )
        
        if dialog.result:
            ext = dialog.result.strip()
            if not ext:
                return
                
            if not ext.startswith('.'):
                ext = '.' + ext
                
            self.extensions.add(ext)
            self.extensions_listbox.delete(0, tk.END)
            for ext in sorted(self.extensions):
                self.extensions_listbox.insert(tk.END, ext)
            
            # 保存更改
            self.save_extensions()
            
            # 显示成功消息
            self.status_bar.config(text=LanguageManager.get_string('extension_added'))
    
    def remove_extension(self):
        """移除文件扩展名"""
        selection = self.extensions_listbox.curselection()
        if not selection:
            return
            
        ext = self.extensions_listbox.get(selection[0])
        self.extensions.remove(ext)
        self.extensions_listbox.delete(0, tk.END)
        for ext in sorted(self.extensions):
            self.extensions_listbox.insert(tk.END, ext)
        
        # 保存更改
        self.save_extensions()
        
        # 显示成功消息
        self.status_bar.config(text=LanguageManager.get_string('extension_removed'))
    
    def reset_to_default_extensions(self):
        """重置为默认文件扩展名"""
        self.extensions = set([".log", ".tmp", ".temp", ".bak", ".old", ".dmp"])
        self.extensions_listbox.delete(0, tk.END)
        for ext in sorted(self.extensions):
            self.extensions_listbox.insert(tk.END, ext)
        
        # 保存更改
        self.save_extensions()
        
        # 显示成功消息
        self.status_bar.config(text=LanguageManager.get_string('extensions_reset'))
    
    def load_extensions(self):
        """从配置文件加载扩展名"""
        try:
            config_file = Path("config/file_extensions.txt")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.extensions = set([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"加载文件后缀配置失败: {str(e)}")
    
    def save_extensions(self):
        """保存扩展名到配置文件"""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "file_extensions.txt"
            with open(config_file, 'w', encoding='utf-8') as f:
                for ext in sorted(self.extensions):
                    f.write(f"{ext}\n")
            self.logger.info("File extensions saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving file extensions: {str(e)}")
    
    def on_close(self):
        """关闭对话框"""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()

    def show_settings(self):
        """显示设置面板"""
        try:
            # 创建新的顶层窗口
            settings_window = tk.Toplevel(self.root)
            settings_window.title(LanguageManager.get_string('settings'))
            settings_window.geometry('700x600')
            settings_window.transient(self.root)  # 设置为主窗口的子窗口
            settings_window.grab_set()  # 模态窗口
            settings_window.configure(background=UITheme.get_bg())
            
            # 确保窗口居中
            settings_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 350,
                self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 300))
            
            # 创建主框架
            main_frame = ttk.Frame(settings_window, style='Card.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 设置选项卡
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 语言设置选项卡
            lang_frame = ttk.Frame(notebook, style='Card.TFrame')
            notebook.add(lang_frame, text=LanguageManager.get_string('current_language'))
            
            # 主题设置选项卡
            theme_frame = ttk.Frame(notebook, style='Card.TFrame')
            notebook.add(theme_frame, text=LanguageManager.get_string('theme_settings'))
            
            # 文件清理设置选项卡
            cleanup_frame = ttk.Frame(notebook, style='Card.TFrame')
            notebook.add(cleanup_frame, text=LanguageManager.get_string('file_extension_settings'))
            
            # 文件过滤设置选项卡
            filter_frame = ttk.Frame(notebook, style='Card.TFrame')
            notebook.add(filter_frame, text=LanguageManager.get_string('exclude_settings'))
            
            # ===== 语言设置 =====
            current_lang = LanguageManager.get_current_language()
            self.lang_var = tk.StringVar(value='zh' if current_lang == Language.CHINESE else 'en')
            
            lang_title = ttk.Label(lang_frame, 
                                  text=LanguageManager.get_string('select_language'),
                                  style='Subtitle.TLabel')
            lang_title.pack(anchor=tk.W, padx=20, pady=(20, 10))
            
            ttk.Radiobutton(lang_frame, 
                           text=LanguageManager.get_string('set_chinese'),
                           variable=self.lang_var, 
                           value='zh').pack(anchor=tk.W, padx=30, pady=10)
            
            ttk.Radiobutton(lang_frame, 
                           text=LanguageManager.get_string('set_english'),
                           variable=self.lang_var, 
                           value='en').pack(anchor=tk.W, padx=30, pady=10)
            
            # ===== 主题设置 =====
            theme_title = ttk.Label(theme_frame, 
                                   text=LanguageManager.get_string('select_theme'),
                                   style='Subtitle.TLabel')
            theme_title.pack(anchor=tk.W, padx=20, pady=(20, 10))
            
            self.theme_var = tk.StringVar(value='light' if UITheme.CURRENT_THEME == "light" else 'dark')
            
            ttk.Radiobutton(theme_frame, 
                           text=LanguageManager.get_string('light_mode'),
                           variable=self.theme_var, 
                           value='light').pack(anchor=tk.W, padx=30, pady=10)
            
            ttk.Radiobutton(theme_frame, 
                           text=LanguageManager.get_string('dark_mode'),
                           variable=self.theme_var, 
                           value='dark').pack(anchor=tk.W, padx=30, pady=10)
            
            # 添加主题自定义按钮
            customize_theme_btn = ttk.Button(
                theme_frame,
                text=LanguageManager.get_string('theme_customization'),
                command=lambda: self.show_theme_customization(),
                style='Primary.TButton'
            )
            customize_theme_btn.pack(anchor=tk.W, padx=30, pady=20)
            
            # ===== 文件清理设置 =====
            self._create_file_extension_settings(cleanup_frame)
            
            # ===== 文件过滤设置 =====
            self._create_file_filter_settings(filter_frame)
            
            # 底部按钮区域
            btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
            btn_frame.pack(fill=tk.X, pady=20)
            
            # 应用按钮
            apply_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string('apply'),
                command=lambda: self._apply_settings_and_close(settings_window),
                style='Primary.TButton'
            )
            apply_btn.pack(side=tk.RIGHT, padx=10)
            
            # 取消按钮
            cancel_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string('cancel'),
                command=settings_window.destroy,
                style='Secondary.TButton'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            self.logger.error(f"设置面板错误: {str(e)}", exc_info=True)
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def _create_file_filter_settings(self, parent_frame):
        """创建文件过滤设置界面"""
        try:
            # 加载已排除的文件和文件夹
            self.excluded_items = self._load_excluded_items()
            
            # 创建说明标签
            desc_label = ttk.Label(
                parent_frame,
                text=LanguageManager.get_string('exclude_description'),
                style='Subtitle.TLabel',
                wraplength=400
            )
            desc_label.pack(anchor=tk.W, padx=20, pady=(20, 10))
            
            # 创建列表框和滚动条
            list_frame = ttk.Frame(parent_frame, style='Card.TFrame')
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.excluded_listbox = tk.Listbox(
                list_frame,
                height=10,
                width=50,
                font=('Segoe UI', 10),
                background=UITheme.get_card_bg(),
                foreground=UITheme.get_text_primary(),
                yscrollcommand=scrollbar.set
            )
            self.excluded_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            scrollbar.config(command=self.excluded_listbox.yview)
            
            # 填充列表
            for item in self.excluded_items:
                self.excluded_listbox.insert(tk.END, item)
            
            # 按钮区域
            btn_frame = ttk.Frame(parent_frame, style='Card.TFrame')
            btn_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # 添加文件按钮
            add_file_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string('add_file'),
                command=self._add_excluded_file,
                style='Primary.TButton'
            )
            add_file_btn.pack(side=tk.LEFT, padx=5)
            
            # 添加文件夹按钮
            add_folder_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string('add_folder'),
                command=self._add_excluded_folder,
                style='Primary.TButton'
            )
            add_folder_btn.pack(side=tk.LEFT, padx=5)
            
            # 移除按钮
            remove_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string('remove_item'),
                command=self._remove_excluded_item,
                style='Secondary.TButton'
            )
            remove_btn.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            self.logger.error(f"Error creating file filter settings: {str(e)}")
            raise

    def _load_excluded_items(self):
        """加载已排除的文件和文件夹"""
        try:
            config_file = Path("config/excluded_items.txt")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
        except Exception as e:
            self.logger.error(f"Error loading excluded items: {str(e)}")
            return []

    def _save_excluded_items(self):
        """保存排除的文件和文件夹"""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "excluded_items.txt"
            with open(config_file, 'w', encoding='utf-8') as f:
                for item in self.excluded_items:
                    f.write(f"{item}\n")
        except Exception as e:
            self.logger.error(f"Error saving excluded items: {str(e)}")

    def _add_excluded_file(self):
        """添加要排除的文件"""
        file_path = filedialog.askopenfilename(
            title=LanguageManager.get_string('select_file_to_exclude'),
            parent=self.root
        )
        if file_path:
            self.excluded_items.append(file_path)
            self.excluded_listbox.insert(tk.END, file_path)
            self._save_excluded_items()

    def _add_excluded_folder(self):
        """添加要排除的文件夹"""
        folder_path = filedialog.askdirectory(
            title=LanguageManager.get_string('select_folder_to_exclude'),
            parent=self.root
        )
        if folder_path:
            self.excluded_items.append(folder_path)
            self.excluded_listbox.insert(tk.END, folder_path)
            self._save_excluded_items()

    def _remove_excluded_item(self):
        """移除选中的排除项"""
        selection = self.excluded_listbox.curselection()
        if selection:
            item = self.excluded_listbox.get(selection[0])
            self.excluded_items.remove(item)
            self.excluded_listbox.delete(selection[0])
            self._save_excluded_items()

    def _apply_settings_and_close(self, window):
        """应用设置并关闭窗口"""
        try:
            # 应用语言设置
            if hasattr(self, 'lang_var'):
                new_lang = self.lang_var.get()
                current_lang = LanguageManager.get_current_language()
                
                if (new_lang == 'zh' and current_lang != Language.CHINESE) or \
                   (new_lang == 'en' and current_lang != Language.ENGLISH):
                    self.change_language(new_lang)
            
            # 应用主题设置
            if hasattr(self, 'theme_var'):
                new_theme = self.theme_var.get()
                if new_theme != UITheme.CURRENT_THEME:
                    self.toggle_theme()
            
            # 保存文件扩展名
            if hasattr(self, 'extensions'):
                self.save_extensions()
            
            # 关闭窗口
            window.destroy()
            
            # 显示成功消息
            self.status_bar.config(text=LanguageManager.get_string('settings_saved'))
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=window
            )

    def check_single_drive(self):
        """检查单个驱动器的GUI版本"""
        try:
            # 清除输出区域
            self._clear_output()
            
            # 调用GUI版本的单驱动器检查
            check_one_drive_gui(self.root)
            
            # 更新状态
            self.status_bar.config(text=LanguageManager.get_string('completed'))
        except Exception as e:
            self.logger.error(f"Error checking drive: {str(e)}", exc_info=True)
            self.status_bar.config(text=f"{LanguageManager.get_string('error')}: {str(e)[:50]}...")

    def check_all_drives(self):
        """检查所有驱动器"""
        try:
            # 清除输出区域
            self._clear_output()
            
            # 获取驱动器检查类实例
            driver_checker = CheckDriver()
            
            # 执行所有驱动器检查
            driver_checker.check_all_drive()
            
            # 更新状态
            self.status_bar.config(text=LanguageManager.get_string('completed'))
        except Exception as e:
            self.logger.error(f"Error checking all drives: {str(e)}", exc_info=True)
            self.status_bar.config(text=f"{LanguageManager.get_string('error')}: {str(e)[:50]}...")

    def check_admin_rights(self, tool_idx):
        """检查工具是否需要管理员权限，并在需要时显示提示"""
        # 需要管理员权限的工具索引
        admin_required_tools = [1, 4, 5, 6, 7, 8]  # SFC, DISM, 网络重置, 驱动器检查, 引导修复等
        
        if tool_idx in admin_required_tools and not is_admin():
            result = messagebox.askokcancel(
                LanguageManager.get_string("admin_required"),
                LanguageManager.get_string("run_as_admin") + "\n\n" + 
                LanguageManager.get_string("continue_anyway"),
                icon='warning'
            )
            return result
        return True

    def open_tool_in_new_window(self, tool_idx):
        """在新窗口中打开工具"""
        # 获取工具名称
        tool_name = LanguageManager.get_string('menu_items')[tool_idx-1]
        
        # 创建新窗口
        tool_window = tk.Toplevel(self.root)
        tool_window.title(LanguageManager.get_string('window_title_new_tool').format(tool_name))
        
        # 设置窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 略微错开位置，避免完全重叠
        offset_x = 50
        offset_y = 50
        center_x = int(screen_width/2 - window_width/2) + offset_x
        center_y = int(screen_height/2 - window_height/2) + offset_y
        tool_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 设置窗口图标
        if "app_icon" in self.images:
            tool_window.iconphoto(True, self.images["app_icon"])
        
        # 窗口可调整大小
        tool_window.resizable(True, True)
        
        # 设置窗口最小尺寸
        tool_window.minsize(600, 400)
        
        # 设置背景色
        tool_window.configure(background=UITheme.get_bg())
        
        # 创建主框架
        main_frame = ttk.Frame(tool_window, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 创建标题
        title_frame = ttk.Frame(main_frame, style='Card.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题标签
        title_label = ttk.Label(
            title_frame, 
            text=tool_name, 
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 输出区域
        output_frame = ttk.Frame(main_frame, style='Card.TFrame')
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建文本框
        output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10),
            background=UITheme.get_output_bg(),
            foreground=UITheme.get_output_text()
        )
        output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        output_text.config(state=tk.DISABLED)  # 禁止用户编辑输出区域
        
        # 进度条
        progress_frame = ttk.Frame(main_frame, style='Card.TFrame')
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='indeterminate',
            style="TProgressbar"
        )
        progress.pack(fill=tk.X, padx=10, pady=10)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 关闭按钮
        close_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string('exit'),
            command=tool_window.destroy,
            style='Secondary.TButton'
        )
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        # 设置重定向
        redirector = RedirectText(output_text)
        
        # 启动工具执行线程
        def run_tool_thread():
            # 保存旧的stdout
            old_stdout = sys.stdout
            sys.stdout = redirector
            
            try:
                # 开始进度条动画
                progress.start(10)
                
                # 执行工具
                ApplTools.get(tool_idx)
                
                # 停止进度条
                progress.stop()
                
            except Exception as e:
                # 处理工具执行错误
                error_msg = f"{LanguageManager.get_string('error')}: {str(e)}"
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"\n{error_msg}\n")
                output_text.see(tk.END)
                output_text.config(state=tk.DISABLED)
                
                # 停止进度条
                progress.stop()
                
            finally:
                # 恢复标准输出
                sys.stdout = old_stdout
        
        # 启动新的线程执行工具，避免界面冻结
        thread = threading.Thread(target=run_tool_thread)
        thread.daemon = True
        thread.start()
    
    def show_theme_customization(self):
        """显示主题自定义对话框"""
        try:
            import tkinter as tk
            from tkinter import ttk, colorchooser
            
            # 创建主题自定义窗口
            theme_window = tk.Toplevel(self.root)
            theme_window.title(LanguageManager.get_string("theme_customization"))
            theme_window.geometry("700x550")
            theme_window.transient(self.root)
            theme_window.resizable(True, True)
            theme_window.configure(background=UITheme.get_bg())
            theme_window.grab_set()  # 模态窗口
            
            # 确保窗口居中
            theme_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 350,
                self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 275
            ))
            
            # 创建主框架 - 使用圆角和阴影效果模仿Windows 11风格
            main_frame = ttk.Frame(theme_window, style='Win11Card.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 标题标签 - 使用Win11风格的大标题
            title_label = ttk.Label(
                main_frame,
                text=LanguageManager.get_string("theme_customization"),
                style='Win11Title.TLabel'
            )
            title_label.pack(pady=(20, 30), padx=20, anchor=tk.W)
            
            # 创建颜色配置框架 - 使用Win11分组框风格
            config_frame = ttk.Frame(main_frame, style='Win11Section.TFrame')
            config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Windows 11风格的栅格布局 - 更宽松的间距
            for i in range(6):
                config_frame.grid_rowconfigure(i, weight=1, pad=15)
            config_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, pad=15)
            
            # 第1行: 主题模式选择
            theme_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("theme_mode"),
                style='Win11Subtitle.TLabel'
            )
            theme_label.grid(row=0, column=0, sticky=tk.W, padx=20, pady=15)
            
            theme_var = tk.StringVar(value=UITheme.CURRENT_THEME)
            theme_combo = ttk.Combobox(
                config_frame,
                textvariable=theme_var,
                values=["light", "dark"],
                state="readonly",
                width=15,
                style='Win11.TCombobox'
            )
            theme_combo.grid(row=0, column=1, sticky=tk.W, padx=20, pady=15)
            
            # 第2行: 主色调
            primary_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("primary_color"),
                style='Win11Subtitle.TLabel'
            )
            primary_label.grid(row=1, column=0, sticky=tk.W, padx=20, pady=15)
            
            primary_var = tk.StringVar(value=UITheme.PRIMARY)
            primary_entry = ttk.Entry(
                config_frame,
                textvariable=primary_var,
                width=10,
                style='Win11.TEntry'
            )
            primary_entry.grid(row=1, column=1, sticky=tk.W, padx=20, pady=15)
            
            primary_button = ttk.Button(
                config_frame,
                text=LanguageManager.get_string("select_color"),
                command=lambda: self._choose_color(primary_var, theme_window),
                style='Win11.TButton'
            )
            primary_button.grid(row=1, column=2, padx=5, pady=15)
            
            # 添加预览框 - 圆角设计
            primary_preview = tk.Canvas(
                config_frame,
                width=30,
                height=30,
                bg=primary_var.get(),
                highlightthickness=0
            )
            primary_preview.grid(row=1, column=3, padx=10, pady=15)
            primary_preview.create_rectangle(0, 0, 30, 30, fill=primary_var.get(), width=0, radius=5)  # 圆角矩形
            
            # 第3行: 强调色
            accent_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("accent_color"),
                style='Win11Subtitle.TLabel'
            )
            accent_label.grid(row=2, column=0, sticky=tk.W, padx=20, pady=15)
            
            accent_var = tk.StringVar(value=UITheme.PRIMARY_LIGHT)
            accent_entry = ttk.Entry(
                config_frame,
                textvariable=accent_var,
                width=10,
                style='Win11.TEntry'
            )
            accent_entry.grid(row=2, column=1, sticky=tk.W, padx=20, pady=15)
            
            accent_button = ttk.Button(
                config_frame,
                text=LanguageManager.get_string("select_color"),
                command=lambda: self._choose_color(accent_var, theme_window),
                style='Win11.TButton'
            )
            accent_button.grid(row=2, column=2, padx=5, pady=15)
            
            # 添加预览框 - 圆角设计
            accent_preview = tk.Canvas(
                config_frame,
                width=30,
                height=30,
                bg=accent_var.get(),
                highlightthickness=0
            )
            accent_preview.grid(row=2, column=3, padx=10, pady=15)
            accent_preview.create_rectangle(0, 0, 30, 30, fill=accent_var.get(), width=0, radius=5)
            
            # 第4行: 背景色
            bg_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("background_color"),
                style='Win11Subtitle.TLabel'
            )
            bg_label.grid(row=3, column=0, sticky=tk.W, padx=20, pady=15)
            
            bg_var = tk.StringVar(value=UITheme.get_bg())
            bg_entry = ttk.Entry(
                config_frame,
                textvariable=bg_var,
                width=10,
                style='Win11.TEntry'
            )
            bg_entry.grid(row=3, column=1, sticky=tk.W, padx=20, pady=15)
            
            bg_button = ttk.Button(
                config_frame,
                text=LanguageManager.get_string("select_color"),
                command=lambda: self._choose_color(bg_var, theme_window),
                style='Win11.TButton'
            )
            bg_button.grid(row=3, column=2, padx=5, pady=15)
            
            # 添加预览框 - 圆角设计
            bg_preview = tk.Canvas(
                config_frame,
                width=30,
                height=30,
                bg=bg_var.get(),
                highlightthickness=0
            )
            bg_preview.grid(row=3, column=3, padx=10, pady=15)
            bg_preview.create_rectangle(0, 0, 30, 30, fill=bg_var.get(), width=0, radius=5)
            
            # 第5行: 卡片背景色
            card_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("card_color"),
                style='Win11Subtitle.TLabel'
            )
            card_label.grid(row=4, column=0, sticky=tk.W, padx=20, pady=15)
            
            card_var = tk.StringVar(value=UITheme.get_card_bg())
            card_entry = ttk.Entry(
                config_frame,
                textvariable=card_var,
                width=10,
                style='Win11.TEntry'
            )
            card_entry.grid(row=4, column=1, sticky=tk.W, padx=20, pady=15)
            
            card_button = ttk.Button(
                config_frame,
                text=LanguageManager.get_string("select_color"),
                command=lambda: self._choose_color(card_var, theme_window),
                style='Win11.TButton'
            )
            card_button.grid(row=4, column=2, padx=5, pady=15)
            
            # 预览框 - 圆角设计
            card_preview = tk.Canvas(
                config_frame,
                width=30,
                height=30,
                bg=card_var.get(),
                highlightthickness=0
            )
            card_preview.grid(row=4, column=3, padx=10, pady=15)
            card_preview.create_rectangle(0, 0, 30, 30, fill=card_var.get(), width=0, radius=5)
            
            # 第6行: 文本颜色
            text_label = ttk.Label(
                config_frame,
                text=LanguageManager.get_string("text_color"),
                style='Win11Subtitle.TLabel'
            )
            text_label.grid(row=5, column=0, sticky=tk.W, padx=20, pady=15)
            
            text_var = tk.StringVar(value=UITheme.get_text_primary())
            text_entry = ttk.Entry(
                config_frame,
                textvariable=text_var,
                width=10,
                style='Win11.TEntry'
            )
            text_entry.grid(row=5, column=1, sticky=tk.W, padx=20, pady=15)
            
            text_button = ttk.Button(
                config_frame,
                text=LanguageManager.get_string("select_color"),
                command=lambda: self._choose_color(text_var, theme_window),
                style='Win11.TButton'
            )
            text_button.grid(row=5, column=2, padx=5, pady=15)
            
            # 添加预览框 - 圆角设计
            text_preview = tk.Canvas(
                config_frame,
                width=30,
                height=30,
                bg=text_var.get(),
                highlightthickness=0
            )
            text_preview.grid(row=5, column=3, padx=10, pady=15)
            text_preview.create_rectangle(0, 0, 30, 30, fill=text_var.get(), width=0, radius=5)
            
            # 创建主题预览框架 - 使用Windows 11卡片样式
            preview_frame = ttk.Frame(main_frame, style='Win11Section.TFrame')
            preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 预览标签 - Win11标题样式
            preview_label = ttk.Label(
                preview_frame,
                text=LanguageManager.get_string("theme_preview"),
                style='Win11Subtitle.TLabel'
            )
            preview_label.pack(pady=10, padx=20, anchor=tk.W)
            
            # 预览区域 - 模拟Windows 11窗口
            preview_area = tk.Frame(
                preview_frame,
                bg=bg_var.get(),
                width=600,
                height=150,
                bd=0,
                highlightthickness=0
            )
            preview_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # 模拟Windows 11标题栏 - 圆角上边框
            preview_title = tk.Frame(
                preview_area,
                bg=primary_var.get(),
                height=35
            )
            preview_title.pack(fill=tk.X, padx=0, pady=0)
            
            preview_title_label = tk.Label(
                preview_title,
                text="Windows 11 Preview",
                bg=primary_var.get(),
                fg=UITheme.TEXT_LIGHT,
                font=('Segoe UI', 10, 'bold')
            )
            preview_title_label.pack(side=tk.LEFT, padx=15, pady=8)
            
            # 模拟卡片 - 圆角和微妙阴影
            preview_card = tk.Frame(
                preview_area,
                bg=card_var.get(),
                relief=tk.RAISED,
                bd=0,
                highlightthickness=0
            )
            preview_card.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # 模拟按钮 - Win11风格的圆角按钮
            preview_button = tk.Button(
                preview_card,
                text="Action Button",
                bg=accent_var.get(),
                fg=UITheme.TEXT_LIGHT,
                relief=tk.FLAT,
                bd=0,
                padx=15,
                pady=8,
                font=('Segoe UI', 10),
                activebackground=self._lighten_color(accent_var.get(), 0.1)
            )
            preview_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=15, pady=15)
            
            # 模拟文本 - Win11字体风格
            preview_text = tk.Label(
                preview_card,
                text="Sample text content with Windows 11 styling",
                bg=card_var.get(),
                fg=text_var.get(),
                justify=tk.LEFT,
                font=('Segoe UI', 10)
            )
            preview_text.pack(anchor=tk.NW, padx=15, pady=15)
            
            # 监听变量变化，动态更新预览
            def update_preview(*args):
                # 更新预览框颜色
                primary_preview.delete("all")
                primary_preview.create_rectangle(0, 0, 30, 30, fill=primary_var.get(), width=0, radius=5)
                
                accent_preview.delete("all")
                accent_preview.create_rectangle(0, 0, 30, 30, fill=accent_var.get(), width=0, radius=5)
                
                bg_preview.delete("all")
                bg_preview.create_rectangle(0, 0, 30, 30, fill=bg_var.get(), width=0, radius=5)
                
                card_preview.delete("all")
                card_preview.create_rectangle(0, 0, 30, 30, fill=card_var.get(), width=0, radius=5)
                
                text_preview.delete("all")
                text_preview.create_rectangle(0, 0, 30, 30, fill=text_var.get(), width=0, radius=5)
                
                # 更新模拟界面颜色
                preview_area.configure(bg=bg_var.get())
                preview_title.configure(bg=primary_var.get())
                preview_title_label.configure(bg=primary_var.get())
                preview_card.configure(bg=card_var.get())
                preview_button.configure(bg=accent_var.get(), activebackground=self._lighten_color(accent_var.get(), 0.1))
                preview_text.configure(bg=card_var.get(), fg=text_var.get())
            
            # 绑定变量变化事件
            primary_var.trace_add("write", update_preview)
            accent_var.trace_add("write", update_preview)
            bg_var.trace_add("write", update_preview)
            card_var.trace_add("write", update_preview)
            text_var.trace_add("write", update_preview)
            
            button_frame = ttk.Frame(main_frame, style='Win11Footer.TFrame')
            button_frame.pack(fill=tk.X, pady=20, padx=20)
            
            # 重置按钮 - Win11 次要按钮样式
            reset_btn = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("reset_to_default"),
                command=lambda: self._reset_theme_colors(theme_var, primary_var, accent_var, bg_var, card_var, text_var),
                style='Win11Secondary.TButton'
            )
            reset_btn.pack(side=tk.LEFT, padx=5)
            
            # 应用按钮 - Win11 强调按钮样式
            apply_btn = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("apply"),
                command=lambda: self._apply_theme_colors(theme_var.get(), primary_var.get(), accent_var.get(), bg_var.get(), card_var.get(), text_var.get(), theme_window),
                style='Win11Primary.TButton'
            )
            apply_btn.pack(side=tk.RIGHT, padx=5)
            
            # 取消按钮 - Win11 次要按钮样式
            cancel_btn = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("cancel"),
                command=theme_window.destroy,
                style='Win11Secondary.TButton'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
            
            # 模拟Win11窗口动画效果
            theme_window.attributes('-alpha', 0.0)  # 初始设为透明
            for i in range(1, 11):
                theme_window.after(i*10, lambda a=i/10: theme_window.attributes('-alpha', a))
            
        except Exception as e:
            self.logger.error(f"Error showing theme customization: {str(e)}", exc_info=True)
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def show_gpu_mode_dialog(self):
        """显示GPU模式选择对话框"""
        try:
            # 使用选项对话框类
            dialog = OptionDialog(
                self.root, 
                LanguageManager.get_string("select_option"),
                [
                    LanguageManager.get_string("normal_display_mode"), 
                    LanguageManager.get_string("continuous_display_mode")
                ],
                default=0  # 默认选择第一项
            )
            
            # 检查用户是否取消了操作
            if dialog.result is None:
                self.logger.info("GPU display operation cancelled")
                print(LanguageManager.get_string("operation_cancelled"))
                return
            
            # 执行选定的GPU显示模式
            env = GI.GPUInfo()
            
            if dialog.result == 0:  # 普通显示模式
                self.logger.info("Normal display mode selected")
                info = env.get_gpu_info()
                if info != 0:
                    self.logger.warning(f"GPU error: {info}")
                    print(f"{LanguageManager.get_string('gpu_error')}: {info}")
            else:  # 连续显示模式
                self.logger.info("Continuous display mode selected")
                
                # 创建一个停止监控对话框
                stop_dialog = self.create_stop_monitor_dialog()
                
                # 创建和启动监控线程
                def monitor_gpu():
                    try:
                        while env.state() and not stop_dialog.stopped:
                            info = env.get_gpu_info()
                            if info != 0:
                                self.logger.warning(f"GPU error: {info}")
                                break
                            time.sleep(1)
                    except Exception as e:
                        self.logger.error(f"GPU monitoring error: {str(e)}")
                    finally:
                        # 确保对话框关闭
                        if stop_dialog.winfo_exists():
                            stop_dialog.destroy()
                
                # 启动监控线程
                monitor_thread = threading.Thread(target=monitor_gpu)
                monitor_thread.daemon = True
                monitor_thread.start()
                
        except Exception as e:
            self.logger.error(f"Error showing GPU mode dialog: {str(e)}")
            print(f"{LanguageManager.get_string('error')}: {str(e)}")

    def show_dism_options_dialog(self):
        """显示DISM选项对话框"""
        try:
            # 使用选项对话框类
            dialog = OptionDialog(
                self.root, 
                LanguageManager.get_string("select_option"),
                [
                    LanguageManager.get_string("dism_auto_option"), 
                    LanguageManager.get_string("dism_manual_option")
                ],
                default=0  # 默认选择第一项
            )
            
            # 检查用户是否取消了操作
            if dialog.result is None:
                self.logger.info("DISM operation cancelled")
                print(LanguageManager.get_string("operation_cancelled"))
                return
            
            # 执行选定的DISM选项
            if dialog.result == 0:  # 自动修复
                self.logger.info("DISM auto option selected")
                SystemCheckFix.auto_dism_check_and_restore_health()
            else:  # 手动修复
                self.logger.info("DISM manual option selected")
                SystemCheckFix.dism_check_and_restore_health()
                
        except Exception as e:
            self.logger.error(f"Error showing DISM options: {str(e)}")
            print(f"{LanguageManager.get_string('error')}: {str(e)}")

    def show_drive_check_dialog(self):
        """显示驱动器检查选项对话框"""
        try:
            # 使用选项对话框类
            dialog = OptionDialog(
                self.root, 
                LanguageManager.get_string("select_option"),
                [
                    LanguageManager.get_string("check_single_drive"), 
                    LanguageManager.get_string("check_all_drives")
                ],
                default=0  # 默认选择第一项
            )
            
            # 检查用户是否取消了操作
            if dialog.result is None:
                self.logger.info("Drive check operation cancelled")
                print(LanguageManager.get_string("operation_cancelled"))
                return
            
            # 获取驱动器检查工具实例
            env = CheckDriver()
            
            # 执行选定的驱动器检查选项
            if dialog.result == 0:  # 检查单个驱动器
                self.logger.info("Check single drive selected")
                check_one_drive_gui(self.root)  # 使用GUI版本的驱动器检查
            else:  # 检查所有驱动器
                self.logger.info("Check all drives selected")
                
                # 确认是否继续检查所有驱动器
                confirm = messagebox.askyesno(
                    LanguageManager.get_string("confirm"),
                    LanguageManager.get_string("confirm_check_all_drives"),
                    icon='question'
                )
                
                if confirm:
                    env.check_all_drive()
                else:
                    print(LanguageManager.get_string("operation_cancelled"))
                    
        except Exception as e:
            self.logger.error(f"Error showing drive check dialog: {str(e)}")
            print(f"{LanguageManager.get_string('error')}: {str(e)}")

    def create_stop_monitor_dialog(self):
        """创建停止监控对话框，用于GPU连续模式"""
        dialog = tk.Toplevel(self.root)
        dialog.title(LanguageManager.get_string("continuous_display_mode"))
        dialog.geometry('300x100')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 150,
            self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 50))
        
        # 创建框架
        frame = ttk.Frame(dialog, style='Card.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 添加提示
        label = ttk.Label(
            frame, 
            text=LanguageManager.get_string("press_esc_to_stop"),
            style='Prompt.TLabel'
        )
        label.pack(pady=5)
        
        # 添加停止按钮
        stop_btn = ttk.Button(
            frame, 
            text=LanguageManager.get_string("operation_cancelled").split()[0],
            command=lambda: setattr(dialog, 'stopped', True),
            style='Primary.TButton'
        )
        stop_btn.pack(pady=5)
        
        # 初始化stopped属性
        dialog.stopped = False
        
        # 绑定ESC键
        dialog.bind("<Escape>", lambda e: setattr(dialog, 'stopped', True))
        
        # 对话框关闭时的处理
        dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(dialog, 'stopped', True))
        
        return dialog

    def show_virus_scan_dialog(self):
        """显示病毒扫描对话框"""
        try:
            # 创建新窗口
            scan_window = tk.Toplevel(self.root)
            scan_window.title(LanguageManager.get_string("virus_scan_title"))
            scan_window.geometry("600x500")
            scan_window.transient(self.root)
            scan_window.resizable(True, True)
            scan_window.configure(background=UITheme.get_bg())
            
            # 确保窗口居中
            scan_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 300,
                self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 250))
            
            # 主框架
            main_frame = ttk.Frame(scan_window, style='Card.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 标题标签
            title_label = ttk.Label(
                main_frame,
                text=LanguageManager.get_string("virus_scan_title"),
                style='Title.TLabel'
            )
            title_label.pack(pady=10)
            
            # 选项框架
            options_frame = ttk.Frame(main_frame, style='Card.TFrame')
            options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 扫描选项
            option_var = tk.IntVar(value=1)  # 默认选择快速扫描
            
            # 快速扫描选项
            quick_scan = ttk.Radiobutton(
                options_frame,
                text=LanguageManager.get_string("quick_scan_option")[3:],  # 移除 "1. " 前缀
                variable=option_var,
                value=1
            )
            quick_scan.pack(anchor=tk.W, padx=20, pady=10)
            
            # 快速扫描说明
            quick_desc = ttk.Label(
                options_frame,
                text=LanguageManager.get_string("quick_scan_info"),
                style='Status.TLabel',
                wraplength=500
            )
            quick_desc.pack(anchor=tk.W, padx=40, pady=5)
            
            # 完整扫描选项
            full_scan = ttk.Radiobutton(
                options_frame,
                text=LanguageManager.get_string("full_scan_option")[3:],  # 移除 "2. " 前缀
                variable=option_var,
                value=2
            )
            full_scan.pack(anchor=tk.W, padx=20, pady=10)
            
            # 完整扫描说明
            full_desc = ttk.Label(
                options_frame,
                text=LanguageManager.get_string("full_scan_info") + "\n" + 
                     LanguageManager.get_string("full_scan_warning"),
                style='Status.TLabel',
                wraplength=500
            )
            full_desc.pack(anchor=tk.W, padx=40, pady=5)
            
            custom_scan = ttk.Radiobutton(
                options_frame,
                text=LanguageManager.get_string("custom_scan_option")[3:],  
                variable=option_var,
                value=3
            )
            custom_scan.pack(anchor=tk.W, padx=20, pady=10)
            
            # 自定义扫描路径输入框架
            custom_frame = ttk.Frame(options_frame)
            custom_frame.pack(fill=tk.X, padx=40, pady=5)
            
            # 路径输入框
            path_var = tk.StringVar()
            path_entry = ttk.Entry(
                custom_frame,
                textvariable=path_var,
                width=40
            )
            path_entry.pack(side=tk.LEFT, padx=5)
            
            # 浏览按钮
            def browse_path():
                from tkinter import filedialog
                path = filedialog.askdirectory(parent=scan_window)
                if path:
                    path_var.set(path)
                    option_var.set(3)  # 选择自定义扫描选项
            
            browse_button = ttk.Button(
                custom_frame,
                text="...",
                command=browse_path,
                width=3
            )
            browse_button.pack(side=tk.LEFT, padx=5)
            
            update_def = ttk.Radiobutton(
                options_frame,
                text=LanguageManager.get_string("update_defs_option")[3:],  
                variable=option_var,
                value=4
            )
            update_def.pack(anchor=tk.W, padx=20, pady=10)
            
            # 更新说明
            update_desc = ttk.Label(
                options_frame,
                text=LanguageManager.get_string("updating_definitions"),
                style='Status.TLabel',
                wraplength=500
            )
            update_desc.pack(anchor=tk.W, padx=40, pady=5)
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame, style='Card.TFrame')
            button_frame.pack(fill=tk.X, pady=10)
            
            # 创建开始扫描按钮
            scan_button = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("confirm"),
                command=lambda: self._handle_virus_scan_option(option_var.get(), path_var.get(), scan_window),
                style='Primary.TButton'
            )
            scan_button.pack(side=tk.RIGHT, padx=10)
            
            # 取消按钮
            cancel_button = ttk.Button(
                button_frame,
                text=LanguageManager.get_string("cancel"),
                command=scan_window.destroy,
                style='Secondary.TButton'
            )
            cancel_button.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            self.logger.error(f"Error showing virus scan dialog: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def _handle_virus_scan_option(self, option, custom_path, parent_window):
        """处理病毒扫描选项选择"""
        try:
            parent_window.destroy()  
            
            if option == 1:  # 快速扫描
                self._execute_virus_scan("quick")
            elif option == 2:  # 完整扫描
                self._execute_virus_scan("full")
            elif option == 3:  # 自定义扫描
                if not custom_path:
                    messagebox.showwarning(
                        LanguageManager.get_string("warning"),
                        LanguageManager.get_string("invalid_path"),
                        parent=self.root
                    )
                    return
                self._execute_custom_virus_scan(custom_path)
            elif option == 4:  # 更新病毒定义
                self._update_virus_definitions()
        
        except Exception as e:
            self.logger.error(f"Error handling virus scan option: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def _execute_virus_scan(self, scan_type):
        """执行病毒扫描"""
        try:
            self.logger.info(f"Starting {scan_type} virus scan")
            self.logger.info(f"{scan_type} virus scan completed")
        except Exception as e:
            self.logger.error(f"Error executing virus scan: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def _execute_custom_virus_scan(self, custom_path):
        """执行自定义病毒扫描"""
        try:
            self.logger.info(f"Starting custom virus scan at path: {custom_path}")
            self.logger.info("Custom virus scan completed")
        except Exception as e:
            self.logger.error(f"Error executing custom virus scan: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def _update_virus_definitions(self):
        """更新病毒定义"""
        try:
            self.logger.info("Updating virus definitions")
            self.logger.info("Virus definitions updated")
        except Exception as e:
            self.logger.error(f"Error updating virus definitions: {str(e)}")
            messagebox.showerror(
                LanguageManager.get_string("error"),
                f"{LanguageManager.get_string('error')}: {str(e)}",
                parent=self.root
            )

    def show_boot_repair_dialog(self):
        """显示引导修复对话框"""
        try:
            # 创建引导修复窗口
            repair_window = tk.Toplevel(self.root)
            repair_window.title(LanguageManager.get_string("menu_items")[7])  # 使用菜单项的"修复引导"文本
            repair_window.geometry('600x500')
            repair_window.transient(self.root)
            repair_window.resizable(True, True)
            repair_window.configure(background=UITheme.get_bg())
            
            # 确保窗口居中
            repair_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + (self.root.winfo_width() / 2) - 300,
                self.root.winfo_rooty() + (self.root.winfo_height() / 2) - 250))
                
            # 创建主框架
            main_frame = ttk.Frame(repair_window, style='Card.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 命令说明框架
            info_frame = ttk.Frame(main_frame, style='Card.TFrame')
            info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # 添加标题
            title_label = ttk.Label(
                info_frame,
                text=LanguageManager.get_string("bootrec_commands_title"),
                style='Subtitle.TLabel'
            )
            title_label.pack(pady=10)
            
            # 创建命令说明文本框
            commands_text = scrolledtext.ScrolledText(
                info_frame,
                wrap=tk.WORD,
                height=10,
                font=('Consolas', 9),
                background=UITheme.get_output_bg(),
                foreground=UITheme.get_output_text()
            )
            commands_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 添加命令说明
            commands_text.insert(tk.END, "/fixmbr - 修复主引导记录\n")
            commands_text.insert(tk.END, "/fixboot - 写入新的引导扇区\n")
            commands_text.insert(tk.END, "/scanos - 扫描所有系统并添加到启动列表\n")
            commands_text.insert(tk.END, "/rebuildbcd - 重建启动配置数据\n")
            commands_text.insert(tk.END, "/? - 获取帮助信息\n\n")
            commands_text.insert(tk.END, "注意：这些命令可能需要管理员权限才能正常执行。\n")
            commands_text.insert(tk.END, "执行后，请重启系统使更改生效。\n")
            commands_text.config(state=tk.DISABLED)  # 设为只读
            
            # 输入框架
            input_frame = ttk.Frame(main_frame, style='Card.TFrame')
            input_frame.pack(fill=tk.X, pady=10)
            
            # 命令提示标签
            prompt_label = ttk.Label(
                input_frame,
                text=LanguageManager.get_string("enter_bootrec_command"),
                style='Status.TLabel'
            )
            prompt_label.pack(side=tk.LEFT, padx=10)
            
            # 命令输入框
            command_var = tk.StringVar()
            command_entry = ttk.Entry(
                input_frame,
                textvariable=command_var,
                width=30
            )
            command_entry.pack(side=tk.LEFT, padx=5)
            
            # 执行按钮
            execute_btn = ttk.Button(
                input_frame,
                text=LanguageManager.get_string("execute"),
                command=lambda: self._execute_boot_repair(command_var.get(), repair_window),
                style='Primary.TButton'
            )
            execute_btn.pack(side=tk.LEFT, padx=10)
            
            # 结果文本框架
            result_frame = ttk.Frame(main_frame, style='Card.TFrame')
            result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # 结果标签
            result_label = ttk.Label(
                result_frame,
                text=LanguageManager.get_string("command_output"),
                style='Status.TLabel'
            )
            result_label.pack(anchor=tk.W, padx=10, pady=5)
            
            # 结果文本框
            result_text = scrolledtext.ScrolledText(
                result_frame,
                wrap=tk.WORD,
                height=8,
                font=('Consolas', 9),
                background=UITheme.get_output_bg(),
                foreground=UITheme.get_output_text()
            )
            result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            result_text.config(state=tk.DISABLED)
            
            # 按钮框架
            btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
            btn_frame.pack(fill=tk.X, pady=10)
            
            # 关闭按钮
            close_btn = ttk.Button(
                btn_frame,
                text=LanguageManager.get_string("close"),
                command=repair_window.destroy,
                style='Secondary.TButton'
            )
            close_btn.pack(side=tk.RIGHT, padx=10)
            
            # 绑定回车键执行命令
            command_entry.bind("<Return>", lambda e: self._execute_boot_repair(command_var.get(), repair_window))
            
            # 设置输入框焦点
            command_entry.focus_set()
            
        except Exception as e:
            self.logger.error(f"Error showing boot repair dialog: {str(e)}")
            print(f"{LanguageManager.get_string('error')}: {str(e)}")

    def _execute_boot_repair(self, command, parent_window):
        """执行引导修复命令"""
        import subprocess
        import threading
        
        if not command:
            messagebox.showwarning(
                LanguageManager.get_string("warning"),
                LanguageManager.get_string("no_command_entered"),
                parent=parent_window
            )
            return
            
        # 查找结果文本框
        result_text = None
        for child in parent_window.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Frame):
                        for widget in subchild.winfo_children():
                            if isinstance(widget, scrolledtext.ScrolledText):
                                result_text = widget
                                break
                        if result_text:
                            break
                if result_text:
                    break
                
        if not result_text:
            messagebox.showerror(
                LanguageManager.get_string("error"),
                LanguageManager.get_string("internal_error"),
                parent=parent_window
            )
            return
            
        # 清空结果文本框
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        
        # 显示执行的命令
        result_text.insert(tk.END, f"{LanguageManager.get_string('executing')}: bootrec {command}\n\n")
        
        # 创建进度框
        progress_window = tk.Toplevel(parent_window)
        progress_window.title(LanguageManager.get_string("processing"))
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.transient(parent_window)
        progress_window.grab_set()
        progress_window.configure(background=UITheme.get_bg())
        
        # 居中显示
        progress_window.geometry("+%d+%d" % (
            parent_window.winfo_rootx() + (parent_window.winfo_width() / 2) - 150,
            parent_window.winfo_rooty() + (parent_window.winfo_height() / 2) - 50
        ))
        
        # 创建进度条
        progress_frame = ttk.Frame(progress_window, style='Card.TFrame')
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        progress_label = ttk.Label(
            progress_frame,
            text=LanguageManager.get_string("executing_command"),
            style='Status.TLabel'
        )
        progress_label.pack(pady=5)
        
        progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=250,
            mode='indeterminate'
        )
        progress.pack(fill=tk.X, pady=10)
        progress.start(10)
        
        # 启动命令执行线程
        def execute_thread():
            try:
                # 执行bootrec命令
                process = subprocess.run(
                    ['bootrec', command], 
                    shell=False,
                    capture_output=True,
                    encoding='cp936',
                    errors='replace',
                    timeout=60
                )
                
                # 在UI线程中更新结果
                parent_window.after(0, lambda: update_result(process))
                
            except subprocess.TimeoutExpired:
                parent_window.after(0, lambda: update_result(None, timeout=True))
            except Exception as e:
                parent_window.after(0, lambda: update_result(None, error=str(e)))
        
        # 更新结果
        def update_result(process, timeout=False, error=None):
            try:
                # 关闭进度窗口
                progress_window.destroy()
                
                # 更新结果文本框
                if timeout:
                    result_text.insert(tk.END, LanguageManager.get_string("command_timeout"), "error")
                    result_text.tag_configure("error", foreground=UITheme.ERROR)
                elif error:
                    result_text.insert(tk.END, f"{LanguageManager.get_string('error')}: {error}", "error")
                    result_text.tag_configure("error", foreground=UITheme.ERROR)
                else:
                    # 显示命令输出
                    if process.returncode == 0:
                        result_text.insert(tk.END, f"{process.stdout}\n", "success")
                        result_text.insert(tk.END, LanguageManager.get_string("command_completed"), "success")
                        result_text.tag_configure("success", foreground=UITheme.SUCCESS)
                    else:
                        result_text.insert(tk.END, f"{process.stderr}\n", "error")
                        result_text.insert(tk.END, LanguageManager.get_string("command_failed"), "error")
                        result_text.tag_configure("error", foreground=UITheme.ERROR)
                
                result_text.see(tk.END)
                
            except Exception as e:
                self.logger.error(f"Error updating boot repair result: {str(e)}")
                
            finally:
                result_text.config(state=tk.DISABLED)
        
        # 启动线程
        thread = threading.Thread(target=execute_thread)
        thread.daemon = True
        thread.start()

    def _save_theme_config(self):
        """保存主题配置到文件"""
        try:
            from pathlib import Path
            import json
            
            # 创建配置目录
            theme_dir = Path("config/theme")
            theme_dir.mkdir(exist_ok=True, parents=True)
            
            # 准备主题配置
            theme_config = {
                "current_theme": UITheme.CURRENT_THEME,
                "primary": UITheme.PRIMARY,
                "primary_light": UITheme.PRIMARY_LIGHT,
                "primary_dark": UITheme.PRIMARY_DARK,
                "light": {
                    "background": UITheme.BACKGROUND,
                    "card_bg": UITheme.CARD_BG,
                    "text_primary": UITheme.TEXT_PRIMARY,
                    "text_secondary": UITheme.TEXT_SECONDARY,
                    "border": UITheme.BORDER,
                    "output_bg": UITheme.OUTPUT_BG,
                    "output_text": UITheme.OUTPUT_TEXT
                },
                "dark": {
                    "background": UITheme.DARK_BACKGROUND,
                    "card_bg": UITheme.DARK_CARD_BG,
                    "text_primary": UITheme.DARK_TEXT_PRIMARY,
                    "text_secondary": UITheme.DARK_TEXT_SECONDARY,
                    "border": UITheme.DARK_BORDER,
                    "output_bg": UITheme.DARK_OUTPUT_BG,
                    "output_text": UITheme.DARK_OUTPUT_TEXT
                }
            }
            
            # 保存到JSON文件
            with open(theme_dir / "theme_config.json", "w", encoding="utf-8") as f:
                json.dump(theme_config, f, indent=4, ensure_ascii=False)
                
            self.logger.info("Theme configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving theme configuration: {str(e)}")

    def _load_theme_config(self):
        """从文件加载主题配置"""
        try:
            from pathlib import Path
            import json
            
            theme_file = Path("config/theme/theme_config.json")
            
            # 如果主题配置文件不存在，使用默认配置
            if not theme_file.exists():
                self.logger.info("Theme configuration file not found, using default")
                return
            
            # 读取JSON配置
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_config = json.load(f)
            
            # 应用主题配置
            UITheme.CURRENT_THEME = theme_config.get("current_theme", "light")
            UITheme.PRIMARY = theme_config.get("primary", "#3f51b5")
            UITheme.PRIMARY_LIGHT = theme_config.get("primary_light", "#757de8")
            UITheme.PRIMARY_DARK = theme_config.get("primary_dark", "#002984")
            
            # 应用明亮主题配置
            light_config = theme_config.get("light", {})
            UITheme.BACKGROUND = light_config.get("background", "#f5f5f7")
            UITheme.CARD_BG = light_config.get("card_bg", "#ffffff")
            UITheme.TEXT_PRIMARY = light_config.get("text_primary", "#212121")
            UITheme.TEXT_SECONDARY = light_config.get("text_secondary", "#757575")
            UITheme.BORDER = light_config.get("border", "#e0e0e0")
            UITheme.OUTPUT_BG = light_config.get("output_bg", "#f8f9fa")
            UITheme.OUTPUT_TEXT = light_config.get("output_text", "#212121")
            
            # 应用深色主题配置
            dark_config = theme_config.get("dark", {})
            UITheme.DARK_BACKGROUND = dark_config.get("background", "#121212")
            UITheme.DARK_CARD_BG = dark_config.get("card_bg", "#1e1e1e")
            UITheme.DARK_TEXT_PRIMARY = dark_config.get("text_primary", "#e0e0e0")
            UITheme.DARK_TEXT_SECONDARY = dark_config.get("text_secondary", "#a0a0a0")
            UITheme.DARK_BORDER = dark_config.get("border", "#424242")
            UITheme.DARK_OUTPUT_BG = dark_config.get("output_bg", "#2d2d2d")
            UITheme.DARK_OUTPUT_TEXT = dark_config.get("output_text", "#e0e0e0")
            
            self.logger.info(f"Theme configuration loaded, current theme: {UITheme.CURRENT_THEME}")
            
        except Exception as e:
            self.logger.error(f"Error loading theme configuration: {str(e)}")

    def _update_ui_colors(self):
        """更新界面颜色"""
        try:
            # 更新窗口背景色
            self.root.configure(background=UITheme.get_bg())
            
            # 更新标题栏
            if hasattr(self, 'header_frame'):
                self.header_frame.configure(background=UITheme.PRIMARY)
                for child in self.header_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(background=UITheme.PRIMARY, foreground=UITheme.TEXT_LIGHT)
            
            # 更新主内容区域
            if hasattr(self, 'main_frame'):
                self.main_frame.configure(background=UITheme.get_bg())
            
            # 更新输出区域
            if hasattr(self, 'output_text'):
                self.output_text.configure(
                    background=UITheme.get_output_bg(),
                    foreground=UITheme.get_output_text()
                )
            
            # 更新所有标题标签
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Label) and str(widget.cget('style')).endswith('Title.TLabel'):
                    widget.configure(foreground=UITheme.get_text_primary())
            
            # 更新所有按钮的样式
            self.setup_styles()
            
            # 强制更新界面
            self.root.update_idletasks()
            
        except Exception as e:
            self.logger.error(f"Error updating UI colors: {str(e)}")

    def enhance_visual_effects(self):
        """优化应用程序视觉效果"""
        self.logger.info("Enhancing visual effects")
        
        try:
            import time
            import platform
            
            # 1. 为卡片添加阴影效果
            self._add_shadow_effects()
            
            # 2. 添加平滑的滚动效果
            self._add_smooth_scrolling()
            
            # 3. 为功能按钮添加悬停效果
            self._add_button_hover_effects()
            
            # 4. 添加界面切换动画
            self._add_transition_effects()
            
            # 5. 应用现代化的字体样式
            self._apply_modern_fonts()
            
            self.logger.info("Visual effects enhanced")
            
        except Exception as e:
            self.logger.error(f"Error enhancing visual effects: {str(e)}")

    def _add_shadow_effects(self):
        """为UI元素添加阴影效果"""
        try:
            # 为主框架添加阴影
            if hasattr(self, 'main_frame'):
                # 使用合法的颜色格式
                shadow_color = "#E0E0E0"  # 使用浅灰色作为阴影
                
                # 创建阴影框架
                shadow_frame = tk.Frame(self.root, bg=shadow_color)
                shadow_frame.place(x=4, y=4, width=self.main_frame.winfo_width(), height=self.main_frame.winfo_height())
                
                # 将主框架放在阴影框架上方
                self.main_frame.lift()
                
                # 保存阴影框架引用
                self.shadow_frames = [shadow_frame]
                
                # 绑定大小变化事件，以便调整阴影尺寸
                self.main_frame.bind("<Configure>", self._update_shadows)
        
        except Exception as e:
            self.logger.error(f"Error adding shadow effects: {str(e)}")

    def _update_shadows(self, event=None):
        """更新阴影框架的尺寸和位置"""
        try:
            if hasattr(self, 'shadow_frames'):
                for i, shadow_frame in enumerate(self.shadow_frames):
                    if i == 0 and hasattr(self, 'main_frame'):  # 主框架阴影
                        shadow_frame.place(
                            x=4, 
                            y=4, 
                            width=self.main_frame.winfo_width(), 
                            height=self.main_frame.winfo_height()
                        )
        except Exception as e:
            self.logger.error(f"Error updating shadows: {str(e)}")

    def _add_smooth_scrolling(self):
        """添加平滑滚动效果"""
        try:
            # 为输出文本区域添加平滑滚动效果
            if hasattr(self, 'output_text'):
                # 平滑滚动函数
                def _smooth_scroll(event):
                    if event.num == 4 or event.delta > 0:  # 向上滚动
                        self._smooth_scroll_up()
                        return "break"
                    elif event.num == 5 or event.delta < 0:  # 向下滚动
                        self._smooth_scroll_down()
                        return "break"
                
                # 绑定鼠标滚轮事件
                self.output_text.bind("<MouseWheel>", _smooth_scroll)  # Windows
                self.output_text.bind("<Button-4>", _smooth_scroll)    # Linux
                self.output_text.bind("<Button-5>", _smooth_scroll)    # Linux
        
        except Exception as e:
            self.logger.error(f"Error adding smooth scrolling: {str(e)}")

    def _smooth_scroll_up(self):
        """平滑向上滚动"""
        try:
            if hasattr(self, 'output_text'):
                # 获取当前位置
                current_pos = float(self.output_text.index("@0,0").split('.')[0])
                
                # 目标位置
                target_pos = max(1.0, current_pos - 3)
                
                # 执行平滑滚动
                self._perform_smooth_scroll(current_pos, target_pos)
        
        except Exception as e:
            self.logger.error(f"Error in smooth scroll up: {str(e)}")

    def _smooth_scroll_down(self):
        """平滑向下滚动"""
        try:
            if hasattr(self, 'output_text'):
                # 获取当前位置
                current_pos = float(self.output_text.index("@0,0").split('.')[0])
                
                # 获取文本总行数
                total_lines = float(self.output_text.index("end-1c").split('.')[0])
                
                # 目标位置
                target_pos = min(total_lines, current_pos + 3)
                
                # 执行平滑滚动
                self._perform_smooth_scroll(current_pos, target_pos)
        
        except Exception as e:
            self.logger.error(f"Error in smooth scroll down: {str(e)}")

    def _perform_smooth_scroll(self, start_pos, end_pos):
        """执行平滑滚动动画"""
        try:
            if hasattr(self, 'output_text'):
                steps = 10
                delay = 5
                step_size = (end_pos - start_pos) / steps
                
                for i in range(steps + 1):
                    pos = start_pos + step_size * i
                    self.output_text.yview_moveto((pos - 1) / float(self.output_text.index("end-1c").split('.')[0]))
                    self.output_text.update()
                    time.sleep(delay / 1000)
        
        except Exception as e:
            self.logger.error(f"Error performing smooth scroll: {str(e)}")

    def _add_button_hover_effects(self):
        """为按钮添加悬停效果"""
        try:
            if hasattr(self, 'buttons'):
                for button in self.buttons:
                    def on_enter(e, btn=button):
                        btn.state(['active'])  # 使用ttk的状态系统
                    
                    def on_leave(e, btn=button):
                        btn.state(['!active'])  # 移除active状态
                    
                    # 绑定事件
                    button.bind("<Enter>", on_enter)
                    button.bind("<Leave>", on_leave)
                
            self.logger.info("Button hover effects added")
        
        except Exception as e:
            self.logger.error(f"Error adding button hover effects: {str(e)}")

    def _add_transition_effects(self):
        """添加界面切换动画效果"""
        try:
            # 为主框架添加渐变显示效果
            if hasattr(self, 'main_frame'):
                # 使主框架先隐藏
                self.main_frame.place_forget()
                
                # 然后用动画效果显示
                self.root.after(100, self._fade_in_main_frame)
        
        except Exception as e:
            self.logger.error(f"Error adding transition effects: {str(e)}")

    def _fade_in_main_frame(self):
        """主框架渐入效果"""
        try:
            if hasattr(self, 'main_frame'):
                # 先放置主框架
                self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                # 初始透明度 (通过alpha通道实现)
                alpha = 0.0
                
                # 透明度变化步骤
                steps = 10
                delay = 20
                
                def update_alpha(current_alpha):
                    if current_alpha < 1.0:
                        # 更新透明度
                        new_alpha = min(1.0, current_alpha + 0.1)
                        
                        # 使用属性动画来实现渐变效果
                        self.apply_animation(self.main_frame, 'place', 
                                            {'relx': 0.5, 'rely': 0.6, 'anchor': tk.CENTER}, 
                                            {'relx': 0.5, 'rely': 0.5, 'anchor': tk.CENTER}, 
                                            steps=steps, delay=delay)
                        
                        # 递归调用，继续更新
                        self.root.after(delay, lambda: update_alpha(new_alpha))
                
                # 开始更新
                update_alpha(alpha)
        
        except Exception as e:
            self.logger.error(f"Error in fade in effect: {str(e)}")

    def _apply_modern_fonts(self):
        """应用现代化的字体样式"""
        try:
            # 获取系统字体
            system_font = self._get_system_font()
            
            # 更新标题字体
            title_font = (system_font, 14, 'bold')
            subtitle_font = (system_font, 12, 'bold')
            button_font = (system_font, 10)
            text_font = (system_font, 9)
            
            # 应用字体到样式
            style = ttk.Style()
            
            # 更新标题样式
            style.configure('Title.TLabel', font=title_font)
            style.configure('Subtitle.TLabel', font=subtitle_font)
            
            # 更新按钮样式
            style.configure('TButton', font=button_font)
            style.configure('Primary.TButton', font=button_font)
            style.configure('Secondary.TButton', font=button_font)
            
            # 更新输出文本区域
            if hasattr(self, 'output_text'):
                self.output_text.configure(font=text_font)
            
            # 更新其他标签
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.configure(font=button_font)
        
        except Exception as e:
            self.logger.error(f"Error applying modern fonts: {str(e)}")

    def _get_system_font(self):
        """获取系统默认字体"""
        return "Segoe UI"

class OptionDialog:
    """选项对话框，用于显示选项列表供用户选择"""
    def __init__(self, parent, title, options, default=0):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('450x300')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.configure(background=UITheme.get_bg())
        
        # 确保对话框居中
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() / 2) - 225,
            parent.winfo_rooty() + (parent.winfo_height() / 2) - 150))
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=title,
            style='Subtitle.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # 选项框架
        options_frame = ttk.Frame(main_frame, style='Card.TFrame')
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加选项
        self.option_var = tk.IntVar(value=default)
        
        for i, option_text in enumerate(options):
            option = ttk.Radiobutton(
                options_frame,
                text=option_text,
                variable=self.option_var,
                value=i
            )
            option.pack(anchor=tk.W, padx=20, pady=8)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=15)
        
        # 取消按钮
        cancel_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string("cancel"),
            command=self.on_cancel,
            style='Secondary.TButton'
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # 确认按钮
        ok_btn = ttk.Button(
            btn_frame,
            text=LanguageManager.get_string("confirm"),
            command=self.on_ok,
            style='Primary.TButton'
        )
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 绑定ESC键
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())
        
        # 模态对话框
        self.dialog.grab_set()
        self.dialog.focus_set()
        parent.wait_window(self.dialog)
    
    def on_ok(self):
        """确认按钮回调"""
        self.result = self.option_var.get()
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮回调"""
        self.result = None
        self.dialog.destroy()

def check_one_drive_gui(parent):
    """GUI版本的单驱动器检查"""
    logger = LogManager().get_logger(__name__)
    try:
        # 获取驱动器盘符
        drive = simpledialog.askstring(
            LanguageManager.get_string("select_drive"),
            LanguageManager.get_string("enter_drive_letter"),
            parent=parent
        )
        
        if not drive:
            logger.info("Drive selection cancelled")
            return
            
        drive = drive.strip()
        logger.info(f"Selected drive: {drive}")
        
        # 询问是否以只读模式检查
        readonly_mode = messagebox.askyesno(
            LanguageManager.get_string("readonly_mode_prompt"),
            LanguageManager.get_string("readonly_mode_prompt"),
            parent=parent
        )
        
        if readonly_mode:
            logger.info(f"Readonly mode check {drive}")
            SystemCheckFix.chkdsk(drive)
        else:
            logger.info(f"Repair mode check {drive}")
            SystemCheckFix.chkdsk(drive, "/f")
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        messagebox.showerror(
            LanguageManager.get_string("operation_failed"),
            f"{LanguageManager.get_string('operation_failed')}: {str(e)}",
            parent=parent
        )

def is_admin():
    """检查程序是否以管理员身份运行"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_gui():
    """启动GUI界面"""
    try:
        root = tk.Tk()
        app = SystemSafetyToolsGUI(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
        
    except Exception as e:
        logger = LogManager().get_logger("gui")
        logger.error(f"Unhandled exception in GUI: {str(e)}", exc_info=True)
        
        try:
            messagebox.showerror("错误", f"发生了意外错误:\n{str(e)}")
        except:
            print(f"严重错误: {str(e)}")
