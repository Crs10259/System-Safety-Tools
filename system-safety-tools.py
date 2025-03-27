import os
import sys
import traceback
from log_utils import LogManager
from config.settings_manager import SettingsManager
from user_interface import run_gui  

def main():
    """主函数"""
    try:
        # 初始化日志记录器
        logger = LogManager().get_logger(__name__)
        logger.info("Starting SystemSafetyTools")
        
        # 初始化设置
        SettingsManager()
        
        # 启动GUI界面
        run_gui()
        
    except Exception as e:
        # 记录未捕获的异常
        if 'logger' in locals():
            logger.error("Unhandled exception:", exc_info=True)
        else:
            print(f"Error initializing application: {str(e)}")
            print(traceback.format_exc())
        
        # 如果GUI还没启动，显示简单的错误消息
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("Error", f"Application initialization error: {str(e)}")
            root.destroy()
        except:
            # 如果无法显示GUI错误，则使用控制台
            print("Failed to show error dialog.")

if __name__ == "__main__":
    main()