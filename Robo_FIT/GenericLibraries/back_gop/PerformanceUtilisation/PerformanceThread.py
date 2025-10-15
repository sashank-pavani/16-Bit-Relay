from threading import Thread
from datetime import datetime
from time import sleep

from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.MemoryUtilisation.AndroidUtilisation.AndroidMemory import AndroidMemory


class PerformanceThread(Thread):
    __t_name = "Default_Name_{}".format(datetime.now().strftime("%H_%M_%S"))

    def __init__(self, config_path):
        super().__init__()
        self.android_mem = AndroidMemory(config_path=config_path)

    def set_test_case_name(self, test_case_name):
        PerformanceThread.__t_name = test_case_name

    def stop_android_mem_log(self):
        self.android_mem.stop_android_mem_data()

    def run(self):
        self.android_mem.get_android_mem_data(test_case_name=PerformanceThread.__t_name)

    def check_status_performance_thread(self) -> bool:
        if self.is_alive():
            return True
        else:
            self.run()
            sleep(5)
            if self.is_alive():
                return True
            return False
