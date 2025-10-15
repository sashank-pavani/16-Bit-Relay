from abc import ABC, abstractmethod


class IPps(ABC):

    @abstractmethod
    def perform_pps_on(self):
        """
        This method is used to make PPS ON
        :return: None
        """
        pass

    @abstractmethod
    def perform_pps_off(self):
        """
        This method is used to make PPS OFF
        :return: None
        """
        pass

    @abstractmethod
    def initialize_pps(self):
        """
        This method is use to initialize the PPS which means make if PPS ON make it OFF and then ON
        :return: None
        """
        pass

    @abstractmethod
    def set_output_voltage(self, voltage_value: str):
        """
        This method is used to set the output voltage of PPS.
        :param voltage_value: String value of voltage. For ex. for setting voltage 8V, then value should be "08.00"
        :return: None
        """
        pass

    @abstractmethod
    def get_voltage_value(self):
        """
        This method return the current value of voltage.
        :return: current voltage value in String
        """
        pass

    @abstractmethod
    def set_output_current(self, current_value):
        """
        This method set the given current value of PPS
        :param current_value: Value of the current which need to be set
        :return: None
        """
        pass

    @abstractmethod
    def get_current_value(self):
        """
        This method is used to get the current value of current.
        :return: Current Value in String format
        """
        pass
