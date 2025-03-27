import os
import time
import subprocess
from log_utils import LogManager
from languages.language_config import LanguageManager
from config.timeout_config import TimeoutConfig

logger = LogManager().get_logger(__name__)

class SystemCheckFix:
    def __init__(self):
        pass

    @staticmethod
    def sfc_scannow():
        """使用系统文件检查器扫描系统文件并修复问题"""
        try:
            logger.info("Running system file checker (sfc /scannow)")
            print(LanguageManager.get_string("running_sfc_scannow"))
            print(LanguageManager.get_string("please_wait"))
            
            # 使用 subprocess.run 而不是 Popen，以简化实现
            process = subprocess.run(
                ['sfc', '/scannow'], 
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=3600  # 1小时超时
            )
            
            # 分析执行结果
            if process.returncode == 0:
                logger.info("System file checker completed successfully")
                if "Windows Resource Protection did not find any integrity violations" in process.stdout:
                    print(LanguageManager.get_string("sfc_no_violations"))
                else:
                    print(LanguageManager.get_string("sfc_completed_violations"))
                    choice = input(LanguageManager.get_string("fix_system_integrity")).lower()
                    if choice == "y":
                        SystemCheckFix.dism_check_and_restore_health()
            else:
                logger.error(f"SFC failed with return code: {process.returncode}")
                logger.error(f"Error output: {process.stderr}")
                print(LanguageManager.get_string("sfc_failed"))
                print(f"{LanguageManager.get_string('error_details')}: {process.stderr}")
                
        except subprocess.TimeoutExpired as e:
            logger.error("SFC operation timed out after 1 hour")
            print(f"{LanguageManager.get_string('subprocess_error')}: {str(e)}")
                
        except FileNotFoundError:
            print(LanguageManager.get_string("sfc_not_found"))
            logger.error("SFC command not found")
        except PermissionError:
            print(LanguageManager.get_string("sfc_permission_denied"))
            logger.error("Permission denied executing SFC")
        except subprocess.SubprocessError as e:
            print(f"{LanguageManager.get_string('subprocess_error')}: {e}")
            logger.error(f"Subprocess error: {e}")
        except Exception as e:
            print(f"{LanguageManager.get_string('unexpected_error')}: {e}")
            logger.error(f"Unexpected error during SFC: {e}")

    @staticmethod
    def chkdsk(drive='C:', action=None):
        """执行磁盘检查"""
        try:
            cmd = ['chkdsk', drive]
            if action:
                cmd.append(action)
            
            process = subprocess.run(
                cmd,
                shell=False,
                check=True,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('chkdsk')
            )
            print(process.stdout)
            logger.info(f"Disk check completed for drive {drive}")
            
        except subprocess.TimeoutExpired:
            logger.error(f"Disk check timed out for drive {drive}")
            print(LanguageManager.get_string("chkdsk_timeout"))
        except subprocess.CalledProcessError as e:
            logger.error(f"Disk check error: {e.stderr}")
            print(f"{LanguageManager.get_string('chkdsk_error')}: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected disk check error: {e}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {e}")

    @staticmethod
    def bootrec(action=''):
        """引导修复"""
        if not action:
            print(LanguageManager.get_string("bootrec_specify_action"))
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            return

        try:
            logger.info(f"Running bootrec {action}")
            process = subprocess.run(
                ['bootrec', action], 
                shell=False, 
                check=True,
                capture_output=True,
                encoding='cp936',
                errors='replace'
            )
            print(f"{LanguageManager.get_string('bootrec_completed')} \n")
            logger.info(f"Bootrec {action} completed")

        except subprocess.CalledProcessError as e:
            error_msg = f"{LanguageManager.get_string('bootrec_error')}: {e}"
            print(f"{error_msg} \n")
            logger.error(f"Bootrec error: {e}")
        except Exception as e:
            error_msg = f"{LanguageManager.get_string('unexpected_error')}: {e}"
            print(f"{error_msg} \n")
            logger.error(f"Bootrec error: {e}")

    @staticmethod
    def dism_check_and_restore_health():
        """检查并修复系统映像"""
        try:
            process = subprocess.run(
                ['DISM.exe', '/Online', '/Cleanup-Image', '/RestoreHealth'],
                shell=False,
                check=True,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('dism')
            )
            print(LanguageManager.get_string("system_image_repair_complete"))
            logger.info("System image repair completed")
            
        except subprocess.TimeoutExpired:
            logger.error("DISM operation timed out")
            print(LanguageManager.get_string("dism_timeout"))
        except subprocess.CalledProcessError as e:
            logger.error(f"DISM error: {e.stderr}")
            print(f"{LanguageManager.get_string('dism_error')}: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected DISM error: {e}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {e}")

    @staticmethod
    def auto_dism_check_and_restore_health():
        """自动检查系统健康状态"""
        try:
            # 扫描健康状态
            subprocess.run(
                ['DISM.exe', '/Online', '/Cleanup-Image', '/ScanHealth'], 
                shell=False, 
                check=True,
                capture_output=True,
                encoding='cp936',
                errors='replace' 
            )
            print(f"{LanguageManager.get_string('system_health_scan_complete')} \n")
            logger.info("System health scan completed")

            # 检查健康状态
            result = subprocess.run(
                ['DISM.exe', '/Online', '/Cleanup-Image', '/CheckHealth'], 
                shell=False, 
                check=True,
                capture_output=True,
                encoding='cp936',
                errors='replace'
            )
            logger.info("System health check completed")

            # 根据检查结果决定是否需要修复
            if "未检测到组件存储损坏" not in result.stdout:
                try:
                    subprocess.run(
                        ['DISM.exe', '/Online', '/Cleanup-Image', '/RestoreHealth'], 
                        shell=False, 
                        check=True,
                        capture_output=True,
                        encoding='cp936',
                        errors='replace'
                    )
                    print(f"{LanguageManager.get_string('system_image_repair_complete')} \n")
                    logger.info("System image repair completed")
                except subprocess.CalledProcessError as e:
                    print(f"{LanguageManager.get_string('system_image_repair_error')}: {e} \n")
                    logger.error(f"System image repair error: {e}")
                except Exception as e:
                    print(f"{LanguageManager.get_string('unexpected_error')}: {e} \n")
                    logger.error(f"System image repair error: {e}")
            else:
                print(f"{LanguageManager.get_string('no_corruption_detected')} \n")

        except subprocess.CalledProcessError as e:
            print(f"{LanguageManager.get_string('dism_health_check_error')}: {e} \n")
            logger.error(f"Dism health check error: {e}")
        except Exception as e:
            print(f"{LanguageManager.get_string('unexpected_error')}: {e} \n")
            logger.error(f"Dism health check error: {e}")

    @staticmethod
    def netsh_winsock_reset():
        try:
            # 重置网络套接字目录
            subprocess.run(['netsh', 'winsock', 'reset'], shell=False, check=True, text=True)
            print("网络重置完成。 \n")
            logger.info("Network reset completed")
        except subprocess.CalledProcessError as e:
            print(f"执行网络套接字重置时出错: {e} \n")
            logger.error(f"Network reset error: {e}")
        except Exception as e:
            print(f"发生错误: {e} \n")
            logger.error(f"Network reset error: {e}")

