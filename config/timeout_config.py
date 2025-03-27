"""超时配置模块，用于设置各种操作的超时值"""

class TimeoutConfig:
    """超时配置类"""
    
    # 命令执行超时设置（秒）
    SFC_TIMEOUT = 3600  # 系统文件检查超时：1小时
    DISM_TIMEOUT = 3600  # DISM工具超时：1小时
    CHKDSK_TIMEOUT = 1800  # 磁盘检查超时：30分钟
    BOOTREC_TIMEOUT = 300  # 引导修复超时：5分钟
    NETSH_TIMEOUT = 60  # 网络重置超时：1分钟
    GPU_INFO_TIMEOUT = 10  # GPU信息获取超时：10秒
    
    # 文件操作超时设置（秒）
    FILE_SCAN_TIMEOUT = 300  # 文件扫描超时：5分钟
    FILE_DELETE_TIMEOUT = 120  # 文件删除操作超时：2分钟
    
    # 输入操作超时设置（秒）
    USER_INPUT_TIMEOUT = 60  # 用户输入超时：1分钟
    
    # 病毒扫描相关超时设置
    QUICK_SCAN_TIMEOUT = 600  # 10分钟
    FULL_SCAN_TIMEOUT = 7200  # 2小时
    CUSTOM_SCAN_TIMEOUT = 1800  # 30分钟
    UPDATE_DEFINITIONS_TIMEOUT = 300  # 5分钟
    REMOVE_THREATS_TIMEOUT = 300  # 5分钟
    
    @classmethod
    def get_timeout(cls, operation_type):
        """获取指定操作类型的超时值"""
        timeout_map = {
            'sfc': cls.SFC_TIMEOUT,
            'dism': cls.DISM_TIMEOUT,
            'chkdsk': cls.CHKDSK_TIMEOUT,
            'bootrec': cls.BOOTREC_TIMEOUT,
            'netsh': cls.NETSH_TIMEOUT,
            'gpu_info': cls.GPU_INFO_TIMEOUT,
            'file_scan': cls.FILE_SCAN_TIMEOUT,
            'file_delete': cls.FILE_DELETE_TIMEOUT,
            'user_input': cls.USER_INPUT_TIMEOUT,
            'quick_scan': cls.QUICK_SCAN_TIMEOUT,
            'full_scan': cls.FULL_SCAN_TIMEOUT,
            'custom_scan': cls.CUSTOM_SCAN_TIMEOUT,
            'update_definitions': cls.UPDATE_DEFINITIONS_TIMEOUT,
            'remove_threats': cls.REMOVE_THREATS_TIMEOUT,
        }
        
        return timeout_map.get(operation_type, 60)  # 默认60秒 