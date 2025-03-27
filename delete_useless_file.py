import os
import os
import ctypes
import win32file
from typing import List
from pathlib import Path
from log_utils import LogManager
from languages.language_config import LanguageManager as lang
import time

# 获取日志记录器实例
logger = LogManager().get_logger(__name__)

class DeleteUselessFile:
    """
    清理工具类，用于管理系统清理操作
    """
    def __init__(self):
        self.drive_letter = self._get_drive_letter()
        self.logger = LogManager().get_logger(__name__)
        self.logger.info(f"Init cleanup module: {self.drive_letter}")

    @staticmethod
    def _get_drive_letter() -> List[str]:
        """使用Win32 API获取可用驱动器列表"""
        drive_bits = win32file.GetLogicalDrives()
        return [f"{chr(65 + i)}:" for i in range(26) if drive_bits & (1 << i)]

    @staticmethod
    def clean_recycle_bin() -> bool:
        """
        清空Windows回收站
        
        返回值:
            bool: 清理是否成功
        """
            
        try:
            shell32 = ctypes.WinDLL('shell32.dll')
            result = shell32.SHEmptyRecycleBinW(None, None, 0)
            
            if result == 0:
                logger.info("Recycle bin cleaned")
                print(lang.get_string("recycle_bin_cleaned"), '\n')
                return True
            else:
                error_code = ctypes.get_last_error()
                logger.error(f"Recycle bin clean failed: {error_code}")
                print(f"{lang.get_string('recycle_bin_clean_failed')}: {error_code} \n")
                return False
                
        except Exception as e:
            logger.error(f"Access recycle bin error': {e}")
            print(f"{lang.get_string('access_recycle_bin_error')}: {e} \n")
            return False

    def delete_log_files(self) -> None:
        """删除指定驱动器中的所有.log文件"""
        for drive in self.drive_letter:
            drive_path = Path(f"{drive}\\")
            if not drive_path.exists():
                continue
                
            try:
                # 添加超时机制
                start_time = time.time()
                timeout = 30  # 30秒超时
                
                for file_path in drive_path.rglob("*.log"):
                    # 检查是否超时
                    if time.time() - start_time > timeout:
                        self.logger.warning(f"Operation timed out on drive {drive}")
                        print(f"{lang.get_string('operation_timeout')}: {drive} \n")
                        break
                        
                    try:
                        # 针对具体的错误进行处理
                        if not file_path.exists():
                            self.logger.warning(f"File does not exist: {file_path}")
                            continue
                            
                        if not os.access(file_path, os.W_OK):
                            self.logger.warning(f"No write permission: {file_path}")
                            print(f"{lang.get_string('no_write_permission')}: {file_path} \n")
                            continue
                            
                        file_path.unlink()
                        self.logger.info(f"Deleted: {file_path}")
                        print(f"{lang.get_string('deleted')}: {file_path} \n")
                        
                    except PermissionError as e:
                        self.logger.error(f"Permission error: {file_path} {e}")
                        print(f"{lang.get_string('permission_error')}: {file_path} {e} \n")
                    except FileNotFoundError as e:
                        self.logger.error(f"File not found: {file_path} {e}")
                        print(f"{lang.get_string('file_not_found')}: {file_path} {e} \n")
                    except OSError as e:
                        self.logger.error(f"OS error: {file_path} {e}")
                        print(f"{lang.get_string('os_error')}: {file_path} {e} \n")
                
            except PermissionError as e:
                self.logger.error(f"Permission error accessing drive: {drive} {e}")
                print(f"{lang.get_string('permission_error_drive')}: {drive} {e} \n")
            except OSError as e:
                self.logger.error(f"OS error accessing drive: {drive} {e}")
                print(f"{lang.get_string('os_error_drive')}: {drive} {e} \n")
            except Exception as e:
                # 只用于捕获其他未预见的异常
                self.logger.error(f"Unexpected error processing drive: {drive} {e}")
                print(f"{lang.get_string('unexpected_error_drive')}: {drive} {e} \n")

    @staticmethod
    def clean_temp_directory() -> None:
        """根据系统环境变量清理临时目录"""
        temp_dir = Path(os.getenv('TEMP', os.getenv('TMP', '/tmp')))
        
        if not temp_dir.exists() or not temp_dir.is_dir():
            logger.error(f"Invalid temp dir: {temp_dir}")
            return
            
        for item in temp_dir.rglob("*"):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
                logger.info(f"Removed: {item}")
                print(f"{lang.get_string('removed')}: {item} \n")
            except (PermissionError, OSError) as e:
                logger.error(f"Remove failed: {item} {e}")
                print(f"{lang.get_string('remove_failed')}: {item} {e} \n")

    @staticmethod
    def get_drive_letters_with_win32file():
        drive_bits = win32file.GetLogicalDrives()
        drive_letters = []
        for i in range(26):  # 共有26个可能的驱动器盘符
            if drive_bits & (1 << i):
                drive_letter = chr(65 + i) + ":\\"
                drive_letters.append(drive_letter)
        
        return drive_letters

    @staticmethod
    def clean_up_recycle_bin(): 
        # 加载 shell32.dll 
        shell32 = ctypes.WinDLL('shell32.dll', use_last_error=True) 
        # 定义 SHEmptyRecycleBin 函数签名 
        SHEmptyRecycleBinA = shell32.SHEmptyRecycleBinA 
        SHEmptyRecycleBinA.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint] 
        SHEmptyRecycleBinA.restype = ctypes.c_long 
        # 调用 SHEmptyRecycleBinA 
        result = SHEmptyRecycleBinA(None, None, 0) 

        # 检查是否成功 
        if result == 0:
            print(lang.get_string("recycle_bin_cleaned"), '\n') 
        else: 
            err = ctypes.get_last_error() 
            print(f"{lang.get_string('recycle_bin_clean_failed')}: {err} \n") 

    def cleanup_system(self) -> None:
        """执行完整的系统清理"""
        try:
            if self.clean_recycle_bin():
                self.logger.info("Recycle bin cleaned")
                print(lang.get_string("recycle_bin_cleaned"), '\n')
            else:
                self.logger.warning("Recycle bin clean failed")
                print(lang.get_string("recycle_bin_clean_failed"), '\n')

            # 清理临时文件
            print(lang.get_string("cleaning_temp_files"), '\n')
            self.logger.info("Cleaning temp files")
            self.clean_temp_directory()

            # 清理日志文件
            print(lang.get_string("cleaning_log_files"), '\n')
            self.logger.info("Cleaning log files")
            self.delete_log_files()
            
        except Exception as e:
            self.logger.error(f"System cleanup error: {str(e)}")
            print(f"{lang.get_string('system_cleanup_error')}: {str(e)} \n")
