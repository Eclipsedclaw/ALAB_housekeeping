# Author: Jiancheng Zeng(JC)
# Date: July 23rd, 2024

from ALABHK_layout import StopFlags
import threading

class test:
    """Placeholder test class with no side effects at definition time."""
    pass


if __name__ == "__main__":
    stop_flags = StopFlags()
    stop_flags.print_flags_status()
    stop_flags.clear_HK_pumping_data()  # Stop data pumping
    stop_flags.print_flags_status()
