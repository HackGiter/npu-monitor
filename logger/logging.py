import logging
import os

# 定义日志文件路径和名称
LOG_DIR = "logs"  # 日志目录
LOG_FILE = "npu_monitor.log"  # 日志文件名

# 创建日志目录，如果不存在
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

def setup_logger(log_level="INFO"):
    """配置日志记录器。"""

    # 创建日志记录器
    logger = logging.getLogger()  # 获取根记录器
    logger.setLevel(logging.DEBUG) # 设置根记录器的最低日志级别为DEBUG，这样所有级别的日志都会被处理

    # 创建文件处理器
    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8') # mode='a' 表示追加模式，utf-8 编码
    file_handler.setLevel(log_level.upper()) # 设置文件处理器的日志级别，根据传入的参数动态设置
    # 创建控制台处理器
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO) # 设置控制台处理器的日志级别为INFO

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 将处理器添加到记录器
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger #返回logger实例

def getLogger(name):
    """获取指定名称的日志记录器。"""
    return logging.getLogger(name)