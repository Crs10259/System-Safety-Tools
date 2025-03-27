import os
import logging
import traceback
from datetime import datetime
from pathlib import Path

class LogManager:
    """管理应用程序日志配置"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LogManager._initialized:
            self._setup_logging()
            LogManager._initialized = True
    
    def _setup_logging(self):
        """配置日志设置"""
        # 如果日志目录不存在则创建
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 使用时间戳生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"system_safety_tools_{timestamp}.log"
        
        # 配置详细的日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s\n'
            'File "%(pathname)s", Line %(lineno)d, in function %(funcName)s'
        )
        
        # 文件处理器，记录详细日志
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        
        # 记录初始信息到文件
        root_logger.info(f"Log file created: {log_file}")
        root_logger.info("system_tools_started")
        
        # 记录系统信息
        self._log_system_info()
    
    def _log_system_info(self):
        """记录基本系统信息"""
        try:
            import platform
            import sys
            logger = logging.getLogger()
            
            system_info = {
                "python_version": sys.version,
                "platform_info": platform.platform(),
                "machine_type": platform.machine(),
                "processor": platform.processor(),
            }
            
            logger.info("system_info")
            for key, value in system_info.items():
                logger.info(f"  {key}: {value}")
            if platform.system() != "Windows":
                logger.warning("non_windows_warning")
                sys.exit(0)

        except Exception as e:
            logging.getLogger().error('collect_system_info_failed: ' + str(e))
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """获取指定名称的日志记录器实例"""
        logger = logging.getLogger(name)
        
        # 添加异常日志记录方法
        def log_exception(exc_info):
            """记录详细的异常信息"""
            logger.error('exception_occurred: ' + str(exc_info))
            logger.error("traceback_info", exc_info=True)
            logger.error('stack_trace:\n' + ''.join(traceback.format_tb(exc_info.__traceback__)))
            
        logger.log_exception = log_exception
        return logger
    
    @staticmethod
    def cleanup_old_logs(max_logs: int = 10, max_days: int = 30):
        """如果日志文件数量超过max_logs或超过max_days天数，则删除旧日志"""
        log_dir = Path("logs")
        if not log_dir.exists():
            return
            
        current_time = datetime.now()
        logger = logging.getLogger()
        
        # 获取所有日志文件并按修改时间排序
        log_files = sorted(
            log_dir.glob("*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # 基于数量和时间清理旧日志
        for log_file in log_files:
            try:
                # 如果超过最大数量则删除
                if len(log_files) > max_logs and log_files.index(log_file) >= max_logs:
                    log_file.unlink()
                    logger.info('deleted_old_log_file: ' + str(log_file))
                    continue
                
                # 如果超过最大天数则删除
                file_age = (current_time - datetime.fromtimestamp(log_file.stat().st_mtime)).days
                if file_age > max_days:
                    log_file.unlink()
                    logger.info('deleted_old_log_file: ' + str(log_file))
                    
            except Exception as e:
                logger.error('delete_old_log_failed ' + str(log_file) + ': ' + str(e)) 