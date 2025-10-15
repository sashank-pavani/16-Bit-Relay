from abc import ABC, abstractmethod
import can
from typing import Union


class ICan(ABC):
    """
    This Class Methods define in CAN Class here we made those methods to abstract methods
    """

    @abstractmethod
    def stop_can_trace(self, data_num) -> None:
        """
        This method is used to stop the CAN signals trace.
        :return: None
        """
        pass

    @abstractmethod
    def send_can_signal_periodically(self, can_des: str, database_num: int = 1, signal_type: str = "TX",
                                     periodicity: int = 100) -> can.CyclicSendTaskABC:
        """
        This method is used to send the CAN signal periodically for a give time interval
        :param signal_type: Type of the signal i.e. Master, TX
        :param can_des: CAN description mention in input File
        :param database_num: database number /channel number
        :param periodicity: Periodic time provided by user in Milisecond in case not provided in input file
        :return: Task object if send the signal otherwise False. Result None.
        """
        pass

    @abstractmethod
    def send_can_signal(self, can_des: str, database_num: int) -> None:
        """
        This method is used to send the CAN signal.
        :param can_des: CAN description mention in InputFile
        :param database_num: CAN description mention in InputFile
        :return: None
        """
        pass

    @abstractmethod
    def stop_can_periodically_signal(self, task: can.CyclicSendTaskABC) -> None:
        """
       This method is used to stop the periodic message.
       :param task: A can.CyclicSendTask object which to be stop
       :return: None
       """
        pass

    @abstractmethod
    def shut_down_can_bus(self, database_num: int) -> None:
        """
        To shout down can bus
        """
        pass

    @abstractmethod
    def receive_can_message_data(self, can_des: str, database_num, timeout=10, is_list: bool = True,
                                 is_dict: bool = False) \
            -> Union[list, dict]:
        """
        This Function Returns Data of Message based on can des provided in CAN_input_Excel.xlsx
        :param can_des: can_des: CAN description in the Excel file
        :param database_num: database number /channel number
        :param timeout: optional, Default value if 10 second. If user required more time than change
        the value in seconds
        :param is_list: data format user want as output in list then make it True else False
        :param is_dict: data format user want as output in list then make it True else False
        :return:list or dict time format output as per is_list or is_dict option selected by user
        """
        pass
