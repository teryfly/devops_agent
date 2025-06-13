# log_config.py
import os
import logging
from datetime import datetime

def setup_logging():
    """配置日志系统，按月份创建二级目录，日志按日期存放"""
    # 基础日志目录
    log_dir = os.path.expanduser("/devops_agent_logs/ai_project_helper_log")
    
    # 创建月份子目录
    today = datetime.now()
    month_dir = today.strftime("%Y-%m")
    full_log_dir = os.path.join(log_dir, month_dir)
    os.makedirs(full_log_dir, exist_ok=True)
    
    # 生成带日期的日志文件名
    log_filename = f"codeing-helper-{today.strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(full_log_dir, log_filename)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("ai_project_helper")

def get_logger(name=None):
    """获取配置好的logger实例"""
    if name:
        return logging.getLogger(f"ai_project_helper.{name}")
    return logging.getLogger("ai_project_helper")