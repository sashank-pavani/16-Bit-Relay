from abc import ABC, abstractmethod


class IUsbSwitch(ABC):

    @abstractmethod
    def connect_usb_switch_port(self, device_name: str):
        """
        This method is used to connect the usb switch port.
        :param device_name: Name of the device which need to connect, This should be as per configuration file
            key "deviceName".
        :return: None
        """
        pass

    @abstractmethod
    def disconnect_usb_switch_port(self, device_name: str):
        """
        This method is used to disconnect the usb switch port.
        :param device_name: Name of the device which need to disconnect, This should be as per configuration file
           key "deviceName".
        :return: None
        """
        pass
