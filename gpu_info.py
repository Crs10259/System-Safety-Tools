import subprocess 
import io_prompts as iop
from languages.language_config import LanguageManager as lang
from log_utils import LogManager

logger = LogManager().get_logger(__name__)

class GPUInfo:
    def __init__(self):
        self.running = True

    def get_gpu_info(self):
        try:
            logger.info("Getting GPU info")
            try:
                # 使用 cp936 编码处理 nvidia-smi 命令输出
                process = subprocess.run(
                    ['cmd.exe', '/c', 'nvidia-smi'], 
                    shell=False, 
                    check=True, 
                    capture_output=True,  # 捕获输出
                    encoding='cp936',     # 使用 Windows 中文编码
                    errors='replace',     # 处理无法解码的字符
                    timeout=10
                )
                print(process.stdout)
                return 0
                
            except subprocess.TimeoutExpired:
                self.running = False
                logger.error("GPU info command timed out")
                print(lang.get_string("gpu_command_timeout"))
                return -1
                
            except subprocess.CalledProcessError as e: 
                iop.clear_screen()
                self.running = False    
                logger.info("Getting GPU basic info")

                try:
                    # 使用 cp936 编码处理 wmic 命令输出
                    result = subprocess.run(
                        ['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                        capture_output=True,
                        encoding='cp936',  # 使用 Windows 中文编码
                        errors='replace',   # 处理无法解码的字符
                        timeout=5
                    )

                    gpu_info = result.stdout.strip().split('\n')[1:]  
                    gpu_info = [info for info in gpu_info if info.strip()]  

                    if gpu_info:
                        logger.info("GPU info found")
                        print(f"\n{lang.get_string('gpu_info')}:")
                        for gpu in gpu_info:
                            print(f"- {gpu.strip()} {lang.get_string('gpu_info_limited')}")
                    else:
                        logger.warning("No GPU info found")
                        print(lang.get_string("gpu_not_found"))
                            
                except subprocess.TimeoutExpired:
                    logger.error("GPU info command (wmic) timed out")
                    print(lang.get_string("gpu_command_timeout"))
                    
                return e
                
        except FileNotFoundError:
            logger.error("GPU info command not found")
            print(lang.get_string("gpu_command_not_found"))
            self.running = False
            return -2
            
        except PermissionError:
            logger.error("Permission denied for GPU info command")
            print(lang.get_string("gpu_permission_denied"))
            self.running = False
            return -3
            
        except Exception as e:
            logger.error(f"Unexpected error getting GPU info: {str(e)}")
            print(f"{lang.get_string('gpu_error')}: {str(e)}")
            self.running = False
            return -4
            
        return 0

    def state(self):
        return self.running   
