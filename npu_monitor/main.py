import curses
import argparse

from npu_monitor import NpuMonitor  # 从包中导入 NpuMonitor
from logger.logging import setup_logger, getLogger # 导入日志配置函数

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NPU monitor tool")
    parser.add_argument("-r", "--refresh-rate", type=float, default=1.0,
                        help="Refresh rate (s), default 1.0")
    parser.add_argument("-l", "--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL), default: INFO")
    args = parser.parse_args()

    # 设置日志记录器
    logger = setup_logger(args.log_level)
    main_logger = getLogger(__name__)

    main_logger.debug("Program running")

    def main(stdscr):
        try:
            monitor = NpuMonitor(stdscr, args.refresh_rate)
            monitor.run()
        except Exception as e:
            main_logger.exception("Exception occured during program running :")
            stdscr.addstr(f"An error occurred: {e}\n")
            stdscr.addstr("Please check the log file for details.\n")
            stdscr.getch() # 等待用户按键，防止窗口立即关闭
    curses.wrapper(main)
    main_logger.debug("Program over")