import os
import sys
import traceback
from log_utils import LogManager
from config.settings_manager import SettingsManager
from user_interface import run_gui

def main():
    """主函数"""
    try:
        logger = LogManager().get_logger(__name__)
        logger.info("Starting SystemSafetyTools")
        
        SettingsManager()
        run_gui()
        
    except Exception as e:
        if 'logger' in locals():
            logger.error("Unhandled exception:", exc_info=True)
        else:
            print(f"Error initializing application: {str(e)}")
            print(traceback.format_exc())
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  
            messagebox.showerror("Error", f"Application initialization error: {str(e)}")
            root.destroy()
        except:
            print("Failed to show error dialog.")

if __name__ == "__main__":
    main()