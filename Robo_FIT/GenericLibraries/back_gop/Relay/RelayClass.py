from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.ConfiguratorManager import ConfiguratorManager
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.IRelay import IRelay
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.ZilogicRelayBoard import ZilogicRelayBoard
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ZILOGIC_RELAY_SWITCH
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug, robot_print_error


class RelayClass(IRelay):

    def __init__(self):
        self.config_manager = ConfiguratorManager()
        self.__initialize_relay()

    def __initialize_relay(self):
        device_name = self.config_manager.get_vendor_name()
        robot_print_debug(f"Initializing Relay for device : {device_name}")
        if device_name == ZILOGIC_RELAY_SWITCH:
            self.current_relay = ZilogicRelayBoard.get_relay_instance()
        else:
            robot_print_error(text=f"Error to initialize the Relay,"
                                   f"\nPlease check the configuration file and provide valid Relay name inside "
                                   f"key 'deviceName'", print_in_report=True, underline=True)
            raise AttributeError("Error to initialize the Relay, Wrong attribute pass in configuration file.")

    def connect_relay_port(self, device_name: str):
        if self.current_relay is None:
            raise TypeError("Relay is not initialize, the object is none. Please check the logs")
        self.current_relay.connect_relay_port(device_name=device_name)

    def disconnect_relay_port(self, device_name):
        if self.current_relay is None:
            raise TypeError("Relay is not initialize, the object is none. Please check the logs")
        self.current_relay.disconnect_relay_port(device_name=device_name)
