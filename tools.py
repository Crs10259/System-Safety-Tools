import time
import msvcrt
import delete_useless_file as DUF
from system_check_fix import SystemCheckFix
import gpu_info as GI
import io_prompts as op
from log_utils import LogManager
from languages.language_config import LanguageManager
import subprocess
import antivirus as AV
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# 使用类一致的方式调用get_string
lang = LanguageManager()

# 获取日志记录器实例
logger = LogManager().get_logger(__name__)

def windows_dism_tools():
    """Windows DISM 工具函数"""
    logger.info("启动 Windows DISM 工具")
    
    try:
        print(LanguageManager.get_string("dism_auto_option"))
        print(LanguageManager.get_string("dism_manual_option"))
        choice = msvcrt.getch()

        if choice.decode() == "1":
            logger.info("DISM auto option")
            SystemCheckFix.auto_dism_check_and_restore_health()
        elif choice.decode() == "2":
            logger.info("DISM manual option")
            SystemCheckFix.dism_check_and_restore_health()
        elif choice == b'\x1b':
            logger.info("Exit DISM tools")
            return
        else:
            logger.warning(f"Invalid choice: {choice}")
            print(LanguageManager.get_string("invalid_choice"))
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('error_occurred')}{str(e)}")

def delete_useless_files():
    """删除无用文件函数"""
    logger.info("Cleaning system")
    try:
        env = DUF.DeleteUselessFile()
        logger.info("Cleaning system")
        env.cleanup_system()
        logger.info("Operation complete")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('operation_failed')}: {str(e)}")

def gpu_basic_info():
    """GPU 信息显示函数"""
    logger.info("GPU basic info")
    try:
        while True:
            print(LanguageManager.get_string("normal_display_mode"))
            print(LanguageManager.get_string("continuous_display_mode"))
            choice = msvcrt.getch()
            env = GI.GPUInfo()
            
            if choice.decode() == "1":
                logger.info("Normal display mode")
                info = env.get_gpu_info()
                if info != 0:
                    logger.warning(f"GPU error: {info}")
                    return
            elif choice.decode() == "2":
                logger.info("Continuous display mode")
                while env.state():
                    info = env.get_gpu_info()
                    if info != 0:
                        logger.warning(f"GPU error: {info}")
                        logger.info("Exit continuous mode")
                        return
                    if msvcrt.getch() == b'\x1b':
                        logger.info("Exit continuous mode")
                        time.sleep(1)
                        break
            elif choice == b'\x1b':
                logger.info("Exit GPU info")
                return
            else:
                logger.warning(f"Invalid choice: {choice}")
                print(LanguageManager.get_string("invalid_choice"))
                time.sleep(3)

    except Exception as e:
        logger.error(f"GPU Error: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('gpu_error')}: {str(e)}")

def sfc_and_delete_useless_files():
    """系统文件检查和清理函数"""
    logger.info("Checking system")
    try:
        op.output(SystemCheckFix.sfc_scannow)
        delete_useless_files()
        logger.info("Operation complete")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('operation_failed')}: {str(e)}")

def user_help():
    """用户帮助函数"""
    logger.info("Help title")
    
    # 获取所有帮助文本
    title = LanguageManager.get_string('help_title')
    help_texts = [
        LanguageManager.get_string('help_input_number'),
        LanguageManager.get_string('help_esc_exit'),
        LanguageManager.get_string('help_settings')
    ]
    
    # 计算标题的实际宽度（考虑中文字符）
    title_width = len(title.encode('gbk'))
    
    # 计算每行帮助文本的填充
    def get_padding(text):
        text_width = len(text.encode('gbk'))
        return ' ' * (title_width - text_width)
    
    # 显示标题和帮助文本
    print(f"\033[1;40;43m{title}\033[0m")
    
    # 显示每行帮助文本，确保与标题对齐
    for help_text in help_texts:
        padding = get_padding(help_text)
        print(f"\n\033[30;106m{help_text}{padding}\033[0m")

class CheckDriver:
    """驱动器检查类"""
    def __init__(self):
        self.env = DUF.DeleteUselessFile()
        self.tools = {"1": self.check_one_drive, "2": self.check_all_drive}
        self.logger = LogManager().get_logger(__name__)
        self.logger.info(LanguageManager.get_string("driver_check_tool_init"))

    def check_all_drive(self):
        """检查所有驱动器"""
        self.logger.info(LanguageManager.get_string("checking_all_drives"))
        try:
            for i in self.env.drive_letter:
                print(f"{LanguageManager.get_string('readonly_mode_prompt')} \n")
                if msvcrt.getch().decode().lower() == 'y':
                    self.logger.info(f"{LanguageManager.get_string('readonly_mode_check')} {i}")
                    SystemCheckFix.chkdsk(i.replace('\\', ''))
                else:
                    self.logger.info(f"{LanguageManager.get_string('repair_mode_check')} {i}")
                    SystemCheckFix.chkdsk(i.replace('\\', ''), "/f")
                time.sleep(5)
        except Exception as e:
            self.logger.error(f"{LanguageManager.get_string('operation_failed')}: {str(e)}", exc_info=True)
            print(f"{LanguageManager.get_string('error_occurred')}{str(e)} \n")

    def check_one_drive(self):
        """检查单个驱动器"""
        logger = LogManager().get_logger(__name__)
        try:
            # 使用GUI输入对话框获取驱动器盘符
            drive = None
            if hasattr(op, 'IN_GUI_MODE') and op.IN_GUI_MODE:
                from user_interface import InputDialog
                dialog = InputDialog(
                    op.get_root_window(),  # 需要添加函数获取主窗口引用
                    LanguageManager.get_string("select_drive"),
                    LanguageManager.get_string("enter_drive_letter")
                )
                drive = dialog.result
            else:
                print(LanguageManager.get_string("select_drive"), '\n')
                drive = input(LanguageManager.get_string("enter_drive_letter")).strip()
            
            if not drive:
                logger.info("Drive selection cancelled")
                return
            
            logger.info(f"Selected drive: {drive}")
            
            # 使用GUI确认对话框询问是否只读模式
            readonly_mode = False
            if hasattr(op, 'IN_GUI_MODE') and op.IN_GUI_MODE:
                from user_interface import ConfirmDialog
                dialog = ConfirmDialog(
                    op.get_root_window(),
                    LanguageManager.get_string("readonly_mode_prompt"),
                    LanguageManager.get_string("readonly_mode_prompt")
                )
                readonly_mode = dialog.result
            else:
                print(LanguageManager.get_string("readonly_mode_prompt"), '\n')
                readonly_mode = msvcrt.getch().decode().lower() == 'y'
            
            if readonly_mode:
                logger.info(f"Readonly mode check {drive}")
                SystemCheckFix.chkdsk(drive)
            else:
                logger.info(f"Repair mode check {drive}")
                SystemCheckFix.chkdsk(drive, "/f")
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}", exc_info=True)
            print(f"{LanguageManager.get_string('operation_failed')}: {str(e)} \n")

    def main(self):
        """主函数"""
        try:
            if len(self.env.get_drive_letters_with_win32file()) == 0:
                self.logger.warning("No drives detected")
                print(LanguageManager.get_string("no_drives_detected"))
                time.sleep(1)
                return
                
            while True:
                print(LanguageManager.get_string("check_single_drive"))
                print(LanguageManager.get_string("check_all_drives"))
                choice = msvcrt.getch()
                
                if choice.decode() not in "12":
                    if choice == b'\x1b':
                        self.logger.info("Exit driver check")
                        return
                    self.logger.warning(f"Invalid choice: {choice}")
                    print(f"{LanguageManager.get_string('invalid_choice')} \n")
                else:
                    self.logger.info(f"Selected option: {choice.decode()}")
                    self.tools[choice.decode()]()
                print("\n")

        except Exception as e:
            self.logger.error(f"Operation failed: {str(e)}", exc_info=True)
            print(f"{LanguageManager.get_string('error_occurred')}{str(e)} \n")

def fix_boot():
    """修复引导函数"""
    logger.info("Start boot repair")
    try:
        print(LanguageManager.get_string("specify_bootrec_operation"), '\n')
        n = input(LanguageManager.get_string("enter_choice")).strip()
        if n == "":
            logger.info("Exit boot repair")
            return
        logger.info(f"Selected boot repair: {n}")
        SystemCheckFix.bootrec(n)
        logger.info("Boot repair complete")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('operation_failed')}: {str(e)}")

def netsh_winsock_reset():
    """网络重置函数"""
    logger.info("Starting network reset")
    
    try:
        # 添加确认提示
        print(LanguageManager.get_string("network_reset_warning"))
        print(LanguageManager.get_string("confirm_network_reset"))
        
        choice = input(LanguageManager.get_string("confirm_y_n")).strip().lower()
        if choice != 'y':
            logger.info("Network reset cancelled by user")
            print(LanguageManager.get_string("operation_cancelled"))
            return
        
        # 使用超时机制执行网络重置
        try:
            process = subprocess.run(
                ['netsh', 'winsock', 'reset'], 
                shell=False, 
                check=True, 
                text=True, 
                timeout=30  # 30秒超时
            )
            
            logger.info("Network reset completed")
            print(LanguageManager.get_string("network_reset_completed"))
            print(LanguageManager.get_string("restart_required"))
            
        except subprocess.TimeoutExpired:
            logger.error("Network reset command timed out")
            print(LanguageManager.get_string("network_reset_timeout"))
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Network reset failed with code {e.returncode}")
            logger.error(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No error output'}")
            print(f"{LanguageManager.get_string('network_reset_failed')}: {e}")
            
    except FileNotFoundError:
        logger.error("Network command not found")
        print(LanguageManager.get_string("network_command_not_found"))
        
    except PermissionError:
        logger.error("Permission denied for network reset")
        print(LanguageManager.get_string("network_permission_denied"))
        print(LanguageManager.get_string("run_as_administrator"))
        
    except Exception as e:
        # 只用于捕获未预见的异常
        logger.error(f"Unexpected error during network reset: {str(e)}")
        print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")

def virus_scan():
    """病毒扫描和查杀功能"""
    logger.info("Starting virus scan tool")
    
    try:
        while True:
            op.clear_screen()
            print(LanguageManager.get_string("virus_scan_title"))
            print(LanguageManager.get_string("scan_options"),)
            print(LanguageManager.get_string("quick_scan_option"))
            print(LanguageManager.get_string("full_scan_option"))
            print(LanguageManager.get_string("custom_scan_option"))
            print(LanguageManager.get_string("update_defs_option"))
            
            choice = msvcrt.getch()
            
            if choice == b'\x1b':  # ESC
                logger.info("Exiting virus scan tool")
                return
                
            if choice.decode() == "1":
                logger.info("Selected quick scan")
                AV.AntivirusScan.run_quick_scan()
                print(LanguageManager.get_string("press_any_key"))
                msvcrt.getch()
                
            elif choice.decode() == "2":
                logger.info("Selected full scan")
                AV.AntivirusScan.run_full_scan()
                print(LanguageManager.get_string("press_any_key"))
                msvcrt.getch()
                
            elif choice.decode() == "3":
                logger.info("Selected custom path scan")
                path = input(LanguageManager.get_string("enter_custom_path")).strip()
                if path:
                    AV.AntivirusScan.run_custom_scan(path)
                print(LanguageManager.get_string("press_any_key"))
                msvcrt.getch()
                
            elif choice.decode() == "4":
                logger.info("Selected update virus definitions")
                AV.AntivirusScan.update_definitions()
                print(LanguageManager.get_string("press_any_key"))
                msvcrt.getch()
                
            else:
                logger.warning(f"Invalid choice: {choice}")
                print(LanguageManager.get_string("invalid_choice"))
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Error in virus scan tool: {str(e)}", exc_info=True)
        print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")
        time.sleep(3)

def check_one_drive_gui(parent):
    """GUI版本的单驱动器检查"""
    logger = LogManager().get_logger(__name__)
    try:
        drive = simpledialog.askstring(
            LanguageManager.get_string("select_drive"),
            LanguageManager.get_string("enter_drive_letter")
        )
        
        if not drive:
            return
            
        logger.info(f"Selected drive: {drive}")
        
        result = messagebox.askyesno(
            LanguageManager.get_string("readonly_mode_prompt"),
            LanguageManager.get_string("readonly_mode_prompt")
        )
        
        if result:
            logger.info(f"Readonly mode check {drive}")
            SystemCheckFix.chkdsk(drive)
        else:
            logger.info(f"Repair mode check {drive}")
            SystemCheckFix.chkdsk(drive, "/f")
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        messagebox.showerror(
            LanguageManager.get_string("operation_failed"),
            f"{LanguageManager.get_string('operation_failed')}: {str(e)}"
        )


