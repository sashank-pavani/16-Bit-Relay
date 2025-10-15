from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ZILOGIC_USB_SWITCH
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.IUsbSwitch import IUsbSwitch
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.ZilogicUsbSwitch import ZilogicUsbSwitch


class UsbSwitch(IUsbSwitch):

    def __init__(self):
        self.config_manager = ConfigurationManager()
        # self.current_usb_switch = None
        self.__initialize_usb_switch()

    def __initialize_usb_switch(self):
        device_name = self.config_manager.get_device_name()
        robot_print_debug(f"Initializing Relay ofr device : {device_name}")
        if device_name == ZILOGIC_USB_SWITCH:
            self.current_usb_switch = ZilogicUsbSwitch.get_serial_instance()
        else:
            robot_print_error(text=f"Error to initialize the USB Switch,"
                                   f"\nPlease check the configuration file and provide valid USB Switch name inside "
                                   f"key 'deviceName'", print_in_report=True, underline=True)
            raise AttributeError("Error to initialize the USB Switch, Wrong attribute pass in configuration file.")

    def connect_usb_switch_port(self, device_name: str):
        if self.current_usb_switch is None:
            raise TypeError("Usb Switch is not initialize, the object is none. Please check the logs")
        robot_print_debug(f"Connecting USB for {device_name}",print_in_report=True)
        self.current_usb_switch.connect_usb_switch_port(device_name=device_name)

    def disconnect_usb_switch_port(self, device_name: str):
        if self.current_usb_switch is None:
            raise TypeError("Usb Switch is not initialize, the object is none. Please check the logs")
        robot_print_debug(f"Disconnecting USB for {device_name}", print_in_report=True)
        self.current_usb_switch.disconnect_usb_switch_port(device_name=device_name)

    def zilogic_switch_host(self, host_number):
        if self.current_usb_switch is None:
            raise TypeError("Usb Switch is not initialize, the object is none. Please check the logs")
        robot_print_debug(f"Connecting host {host_number}", print_in_report=True)
        self.current_usb_switch.switch_host(host_number=str(host_number))
