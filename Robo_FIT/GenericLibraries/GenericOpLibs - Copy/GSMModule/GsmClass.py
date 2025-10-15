from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ASTAR_GSM
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.IGsmModule import IGsmModule
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.AstarGSMModule import AstarGSMModule


class GsmClass(IGsmModule):

    def __init__(self):
        self.current_gsm = None
        self.config_manager = ConfigurationManager()

    def __initialize_gsm(self):
        device_name = self.config_manager.gsm_read_device_name()
        robot_print_debug(f"Initializing GSM for device: {device_name}")
        if device_name == ASTAR_GSM:
            self.current_gsm = AstarGSMModule.get_gsm_instance()
        else:
            robot_print_error(text=f"Error to initialize the GSM,"
                                   f"\nPlease check the configuration file and provide valid GSM name inside "
                                   f"key 'deviceName'", print_in_report=True, underline=True)
            raise AttributeError("Error to initialize the GSM, Wrong attribute pass in configuration file.")

    def gsm_send_message(self, gsm_num, recipient, message):
        if self.current_gsm is None:
            raise TypeError("GSM is not initialize, the object is none. Please check the logs")
        self.current_gsm.gsm_send_message(gsm_num, recipient, message)

    def gsm_make_call(self, gsm_num, recipient):
        if self.current_gsm is None:
            raise TypeError("GSM is not initialize, the object is none. Please check the logs")
        self.current_gsm.gsm_make_call(gsm_num, recipient)

    def gsm_end_call(self, gsm_num):
        if self.current_gsm is None:
            raise TypeError("GSM is not initialize, the object is none. Please check the logs")
        self.current_gsm.gsm_end_call(gsm_num)

    def gsm_answer_call(self, gsm_num):
        if self.current_gsm is None:
            raise TypeError("GSM is not initialize, the object is none. Please check the logs")
        self.current_gsm.gsm_answer_call(gsm_num)

    def gsm_reject_call(self, gsm_num):
        if self.current_gsm is None:
            raise TypeError("GSM is not initialize, the object is none. Please check the logs")
        self.current_gsm.gsm_reject_call(gsm_num)
