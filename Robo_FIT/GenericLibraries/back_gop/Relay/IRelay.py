from abc import ABC, abstractmethod


class IRelay(ABC):

    @abstractmethod
    def connect_relay_port(self, device_name: str):
        """
        This method us use to connect the Ignition port
        :device_name: Name of the device which need to connect, this should be base on the configuration file key
                      "cntDeviceName".
        :return: None
        """
        pass

    @abstractmethod
    def disconnect_relay_port(self, device_name):
        """
        This method us use to connect the Ignition port
        :param device_name: Name of the device which need to connect, this should be base on the configuration file key
                      "cntDeviceName".
        :return:
        """
        pass