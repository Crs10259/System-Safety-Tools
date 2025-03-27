import subprocess
import time
import os
from log_utils import LogManager
from languages.language_config import LanguageManager
from config.timeout_config import TimeoutConfig

logger = LogManager().get_logger(__name__)

class AntivirusScan:
    """系统病毒扫描和查杀功能"""
    
    @staticmethod
    def run_quick_scan():
        """执行快速扫描"""
        try:
            logger.info("Starting quick virus scan")
            print(LanguageManager.get_string("virus_scan_starting"))
            print(LanguageManager.get_string("quick_scan_info"))
            
            process = subprocess.run(
                ['powershell', '-Command', 'Start-MpScan -ScanType QuickScan'],
                shell=False, 
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('quick_scan')
            )
            
            if process.returncode == 0:
                logger.info("Quick scan completed successfully")
                print(LanguageManager.get_string("quick_scan_completed"))
                AntivirusScan._show_scan_results()
            else:
                logger.error(f"Quick scan failed: {process.stderr}")
                print(f"{LanguageManager.get_string('scan_failed')}: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Quick scan timed out")
            print(LanguageManager.get_string("scan_timeout"))
        except FileNotFoundError:
            logger.error("Windows Defender PowerShell commands not found")
            print(LanguageManager.get_string("defender_not_found"))
        except PermissionError:
            logger.error("Permission denied running Windows Defender scan")
            print(LanguageManager.get_string("defender_permission_denied"))
        except Exception as e:
            logger.error(f"Error during quick scan: {str(e)}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")
    
    @staticmethod
    def run_full_scan():
        """执行完整扫描"""
        try:
            logger.info("Starting full virus scan")
            print(LanguageManager.get_string("virus_scan_starting"))
            print(LanguageManager.get_string("full_scan_info"))
            print(LanguageManager.get_string("full_scan_warning"))
            
            process = subprocess.run(
                ['powershell', '-Command', 'Start-MpScan -ScanType FullScan'],
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('full_scan')
            )
            
            if process.returncode == 0:
                logger.info("Full scan completed successfully")
                print(LanguageManager.get_string("full_scan_completed"))
                AntivirusScan._show_scan_results()
            else:
                logger.error(f"Full scan failed: {process.stderr}")
                print(f"{LanguageManager.get_string('scan_failed')}: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Full scan timed out")
            print(LanguageManager.get_string("scan_timeout"))
        except FileNotFoundError:
            logger.error("Windows Defender PowerShell commands not found")
            print(LanguageManager.get_string("defender_not_found"))
        except PermissionError:
            logger.error("Permission denied running Windows Defender scan")
            print(LanguageManager.get_string("defender_permission_denied"))
        except Exception as e:
            logger.error(f"Error during full scan: {str(e)}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")
    
    @staticmethod
    def run_custom_scan(path):
        """执行自定义路径扫描"""
        if not path or not os.path.exists(path):
            logger.error(f"Invalid path for custom scan: {path}")
            print(LanguageManager.get_string("invalid_path"))
            return
            
        try:
            logger.info(f"Starting custom scan on path: {path}")
            print(LanguageManager.get_string("virus_scan_starting"))
            print(f"{LanguageManager.get_string('custom_scan_path')}: {path}")
            
            process = subprocess.run(
                ['powershell', '-Command', f'Start-MpScan -ScanType CustomScan -ScanPath "{path}"'],
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('custom_scan')
            )
            
            if process.returncode == 0:
                logger.info("Custom scan completed successfully")
                print(LanguageManager.get_string("custom_scan_completed"))
                AntivirusScan._show_scan_results()
            else:
                logger.error(f"Custom scan failed: {process.stderr}")
                print(f"{LanguageManager.get_string('scan_failed')}: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Custom scan timed out")
            print(LanguageManager.get_string("scan_timeout"))
        except FileNotFoundError:
            logger.error("Windows Defender PowerShell commands not found")
            print(LanguageManager.get_string("defender_not_found"))
        except PermissionError:
            logger.error("Permission denied running Windows Defender scan")
            print(LanguageManager.get_string("defender_permission_denied"))
        except Exception as e:
            logger.error(f"Error during custom scan: {str(e)}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")

    @staticmethod
    def update_definitions():
        """更新病毒定义"""
        try:
            logger.info("Updating virus definitions")
            print(LanguageManager.get_string("updating_definitions"))
            
            process = subprocess.run(
                ['powershell', '-Command', 'Update-MpSignature'],
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('update_definitions')
            )
            
            if process.returncode == 0:
                logger.info("Virus definitions updated successfully")
                print(LanguageManager.get_string("definitions_updated"))
            else:
                logger.error(f"Failed to update virus definitions: {process.stderr}")
                print(f"{LanguageManager.get_string('update_failed')}: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Update virus definitions timed out")
            print(LanguageManager.get_string("update_timeout"))
        except FileNotFoundError:
            logger.error("Windows Defender PowerShell commands not found")
            print(LanguageManager.get_string("defender_not_found"))
        except PermissionError:
            logger.error("Permission denied updating Windows Defender definitions")
            print(LanguageManager.get_string("defender_permission_denied"))
        except Exception as e:
            logger.error(f"Error updating virus definitions: {str(e)}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}")
    
    @staticmethod
    def _show_scan_results():
        """显示扫描结果"""
        try:
            process = subprocess.run(
                ['powershell', '-Command', 'Get-MpThreatDetection'],
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=30
            )
            
            if process.stdout.strip():
                logger.info("Threats detected")
                print(LanguageManager.get_string("threats_detected"))
                print(process.stdout)
                
                # 询问用户是否要清除威胁
                print(LanguageManager.get_string("remove_threats_prompt"))
                choice = input(LanguageManager.get_string("confirm_y_n")).strip().lower()
                if choice == 'y':
                    AntivirusScan._remove_threats()
            else:
                logger.info("No threats detected")
                print(LanguageManager.get_string("no_threats_detected"))
                
        except Exception as e:
            logger.error(f"Error showing scan results: {str(e)}")
            print(f"{LanguageManager.get_string('results_error')}: {str(e)}")
    
    @staticmethod
    def _remove_threats():
        """移除检测到的威胁"""
        try:
            logger.info("Removing detected threats")
            print(LanguageManager.get_string("removing_threats"))
            
            process = subprocess.run(
                ['powershell', '-Command', 'Remove-MpThreat'],
                shell=False,
                capture_output=True,
                encoding='cp936',
                errors='replace',
                timeout=TimeoutConfig.get_timeout('remove_threats')
            )
            
            if process.returncode == 0:
                logger.info("Threats removed successfully")
                print(LanguageManager.get_string("threats_removed"))
            else:
                logger.error(f"Failed to remove threats: {process.stderr}")
                print(f"{LanguageManager.get_string('removal_failed')}: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Threat removal timed out")
            print(LanguageManager.get_string("removal_timeout"))
        except Exception as e:
            logger.error(f"Error removing threats: {str(e)}")
            print(f"{LanguageManager.get_string('unexpected_error')}: {str(e)}") 