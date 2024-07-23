# Author: Jiancheng Zeng(JC)
# Date: July 23rd, 2024

from ALABHK_layout import StopFlags
import threading

class test:
    stop_flags = StopFlags()
    stop_flags.print_flags_status()
    stop_flags.clear_HK_pumping_data()  # Stop data pumping
    stop_flags.print_flags_status()

