from curses import (
    color_pair,
    init_pair,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_MAGENTA,
    COLOR_YELLOW,
    A_UNDERLINE,
    A_BOLD,
    ERR,
    endwin
)
from collections import namedtuple

NpuData = namedtuple('NpuData', ['index', 'name', 'power', 'temp', 'aicore_used', 'mem_used', 'mem_total', 'hbm_used', 'hbm_total', 'processes'])
Process = namedtuple('Process', ["pid", "name", "mem", "cmd"])

def init_color():
    # Initialize color pairs
    init_pair(1, COLOR_BLUE, COLOR_BLACK)
    init_pair(2, COLOR_GREEN, COLOR_BLACK)  # Green for low temp
    init_pair(3, COLOR_MAGENTA, COLOR_BLACK)  # Magenta for low temp
    init_pair(4, COLOR_YELLOW, COLOR_BLACK)  # Yellow for medium temp
    init_pair(5, COLOR_RED, COLOR_BLACK)  # Red for high temp

def colorize_temp(temp):
    """Returns a curses color pair based on temperature."""
    temp = int(temp)  # Convert temp to integer
    if temp < 40:
        return color_pair(1)  # Blue
    elif temp < 45:
        return color_pair(2)  # Green
    elif temp < 50:
        return color_pair(3)  # Magenta
    elif temp < 55:
        return color_pair(4)  # Yellow
    else:
        return color_pair(5)  # Red
    
def colorize_mem(mem_mb, max_mem):
    """根据内存占用量返回curses颜色对。"""
    if max_mem == 0:  # 避免除以零
        return color_pair(1)  # 默认绿色
    mem_percent = (mem_mb / max_mem) * 100
    if mem_percent < 10:
        return color_pair(1)  # 蓝色
    if mem_percent < 30:
        return color_pair(2)  # 绿色
    elif mem_percent < 60:
        return color_pair(3)  # 品红色
    elif mem_percent < 90:
        return color_pair(4)  # 黄色
    else:
        return color_pair(5)  # 红色

def create_progressbar(percent, width):
    """创建一个简单的文本进度条。"""
    filled_width = int(percent / 100 * width)
    bar = "█" * filled_width + "-" * (width - filled_width) 
    return f"[{bar}] {float(percent):.1f}%"
