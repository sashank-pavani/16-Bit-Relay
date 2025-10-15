from threading import Thread
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidCrashReport.CaptureCrashLogs import CaptureCrashLogs


class CrashLogsThread(Thread):
    __instance = None

    @staticmethod
    def get_crash_log_thread_instance(device_name):
        """
        This method create the Static instance of the CrashLogsThread() class
        :param device_name: device name, who's crash to be monitor
        :return: Instance of CrashLogsThread() class
        """
        if CrashLogsThread.__instance is None:
            CrashLogsThread(device_name)
        return CrashLogsThread.__instance

    def __init__(self, device_name):
        """
        This is constructor  CrashLogsThread() class
        :param device_name: device name, who's crash to be monitor
        :return: None
        """
        if CrashLogsThread.__instance is not None:
            raise Exception("CrashLogsThread is not initialize")
        else:
            super().__init__()
            self.capture_crash_log = CaptureCrashLogs(device_name)
            CrashLogsThread.__instance = self

    def run(self) -> None:
        self.capture_crash_log.start_capture_crash_logs()
        sleep(5)
        # if thread is kill it start the thread again
        CrashLogsThread.__instance = None

    def check_crash_log_thread(self) -> bool:
        """
        This method check android CrashLogsThread() thread is alive or Not
        :return: if thread live return True, otherwise False
        """
        if self.is_alive():
            return True
        else:
            return False
