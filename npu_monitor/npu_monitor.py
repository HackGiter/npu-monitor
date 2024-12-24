import re
import time
import subprocess
from logger.logging import getLogger
from .utils import (
    init_color,
    colorize_temp, 
    colorize_mem, 
    create_progressbar,
    NpuData, 
    Process,
    A_UNDERLINE,
    A_BOLD
)
from .hparam import *

class NpuMonitor:
    def __init__(self, stdscr, refresh_rate):
        self.stdscr = stdscr
        self.refresh_rate = refresh_rate
        self.logger = getLogger(__name__)

    def get_npu_info(self):
        try:
            process = subprocess.run(['npu-smi', 'info'], capture_output=True, text=True, check=True)
            self.logger.debug(f"npu-smi info output:\n{process.stdout}")
            return process.stdout
        except subprocess.CalledProcessError as e:
            error_message = f"Error executing npu-smi: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
            self.logger.error(error_message)
            return f"Error executing npu-smi: {e}"
        except FileNotFoundError:
            error_message = "npu-smi command not found. Please ensure it's installed."
            self.logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            self.logger.exception(error_message)
            return error_message

    def get_process_command(self, pid):
        try:
            with open(f"/proc/{pid}/cmdline", "r") as f:
                cmdline = f.read().replace('\x00', ' ')
                return cmdline.strip()
        except FileNotFoundError:
            return "N/A"
        except Exception as e:
            self.logger.error(f"Error getting command for PID {pid}: {e}")
            return "Error"

    def parse_npu_info(self, output):
        npu_data = []
        npu_regex = r"\| (\d+) +(\w+) +\| OK +\| +([\d.]+) +([\d]+) +.*\|"
        memory_regex = r"\|\s*\d+\s*\|\s*(\d{4}:\w{2}:\d{2}\.\d+)\s*\|\s*(\d+)\s*(\d+)\s*/\s*(\d+)\s*(\d+)\s*/\s*(\d+)\s*\|"
        process_regex = r"\| (\d+) +0 +\| +(\d+) +\| +([\w-]+) +\| +([\d]+) +\|"

        npu_matches = list(re.finditer(npu_regex, output))
        process_matches = re.findall(process_regex, output)

        for i, npu_match in enumerate(npu_matches):
            index, name, power, temp = npu_match.groups()
            mem_used, mem_total, hbm_used, hbm_total = "N/A", "N/A", "N/A", "N/A"

            if i + 1 < len(npu_matches):
                next_line_start = npu_matches[i+1].start()
                current_npu_end = npu_match.end()
                memory_block = output[current_npu_end:next_line_start]
                memory_match = re.search(memory_regex, memory_block)
                if memory_match:
                    bus_id, aicore, mem_used, mem_total, hbm_used, hbm_total = memory_match.groups()
            elif i + 1 == len(npu_matches):
                memory_block = output[npu_match.end():]
                memory_match = re.search(memory_regex, memory_block)
                if memory_match:
                    bus_id, aicore, mem_used, mem_total, hbm_used, hbm_total = memory_match.groups()

            processes = []
            for p_index, pid, process_name, process_mem in process_matches:
                if int(p_index) == int(index):
                    processes.append(Process(pid, process_name, process_mem, self.get_process_command(pid)))

            npu_data.append(NpuData(index, name, power, temp, aicore, mem_used, mem_total, hbm_used, hbm_total, processes))

        return npu_data

    def display_npu_info(self, npu_data):
        self.stdscr.clear()
        rows, cols = self.stdscr.getmaxyx()

        init_color()
        self.stdscr.addstr("NPU Monitor (Press Ctrl+C to quit)\n", A_BOLD)
        npu_info = self.get_npu_info()
        
        if "Error" in npu_info or "not found" in npu_info:
            self.stdscr.addstr("No NPU information available or npu-smi command execution failed.")
            self.stdscr.refresh()
            return

        npu_data = self.parse_npu_info(npu_info)

        PROCESS_WIDTH = cols - NPU_WIDTH - 5
        CMD_WIDTH = cols - (NPU_ID_WIDTH + PID_WIDTH + NAME_WIDTH + MEM_WIDTH + BAR_WIDTH + 10)
        self.logger.debug(PROCESS_WIDTH)
        self.logger.debug(CMD_WIDTH)
        self.logger.debug(cols)
        self.logger.debug(NPU_WIDTH)

        header_format = f"{{:<{NPU_WIDTH}}}|{{:^{TEMP_WIDTH}}}|{{:^{POWER_WIDTH}}}|{{:^{AICORE_WIDTH}}}|{{:^{HBM_WIDTH}}}"
        header_str = header_format.format("NPU", "Temp (°C)", "Power (W)", "AICore Usage (%)", "HBM Usage (MB)")
        self.stdscr.addstr(header_str + "\n", A_UNDERLINE)

        for npu in npu_data:
            temp_celsius = int(float(npu.temp)) #转换成float再转换成int
            temp_celsius_str = str(temp_celsius)
            output_format = f"{{:<{NPU_WIDTH}}}|{{:^{TEMP_WIDTH}}}|{{:^{POWER_WIDTH}}}|{{:^{AICORE_WIDTH}}}|{{:^{HBM_WIDTH}}}"
            self.stdscr.addstr(
                output_format.format(f"{npu.name} {npu.index}", temp_celsius_str, 
                                    str(npu.power), f"{npu.aicore_used}", 
                                    f"{npu.hbm_used:>5}/{npu.hbm_total}") + "\n", colorize_temp(temp_celsius)) #显示index

        process_format = f"{{:<{NPU_ID_WIDTH}}}|{{:^{PID_WIDTH}}}|{{:^{NAME_WIDTH}}}|{{:^{MEM_WIDTH}}}|{{:^{BAR_WIDTH}}}|{{:<{CMD_WIDTH}}}\n"
        self.stdscr.addstr("\nProcesses running:\n")
        if npu_data:
            process_header = f"{'':<{NPU_ID_WIDTH}}| {'Processes Info':<{PROCESS_WIDTH}}" # 第一个空字符串是为了占位NPU索引列
            self.stdscr.addstr(process_header + "\n", A_UNDERLINE)
            self.stdscr.addstr(process_format.format("NPU ID", "PID", "NAME", "MEMORY USAGE (MB)", "AICORE USAGE (%)", "COMMAND LINE"))
            for npu in npu_data:
                npu_index = npu.index #使用npu index
                hbm_total = int(npu.hbm_total)
                hbm_usage = int(npu.hbm_used)
                bar = create_progressbar(int(npu.aicore_used), BAR_WIDTH-10)
                if npu.processes:
                    for process in npu.processes:
                        mem_usage = int(process.mem)
                        cmd = process.cmd
                        cmd = cmd[:CMD_WIDTH-4] + "..." if len(cmd) + 1 > CMD_WIDTH else cmd
                        process_info = process_format.format(
                            f"{npu_index}", 
                            process.pid, 
                            process.name[:NAME_WIDTH], 
                            f"{process.mem} MB",
                            bar,
                            f" {cmd}")
                        self.stdscr.addstr(process_info, colorize_mem(max(hbm_usage, mem_usage), hbm_total))
                        npu_index, bar, hbm_usage = " ", "", 0
                else:
                    self.stdscr.addstr(f"{npu_index:<{NPU_ID_WIDTH}}| No running processes\n", colorize_mem(0, hbm_total)) #输出npu index

        self.stdscr.refresh()

    def run(self):
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)

        while True:
            npu_info_str = self.get_npu_info()
            if "Error" in npu_info_str or "not found" in npu_info_str:
                self.display_npu_info([])  # Display empty data to show error message
            else:
                npu_data = self.parse_npu_info(npu_info_str)
                self.display_npu_info(npu_data)
            time.sleep(self.refresh_rate)

            key = self.stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break