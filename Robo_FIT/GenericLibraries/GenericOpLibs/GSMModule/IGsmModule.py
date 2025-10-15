from abc import ABC, abstractmethod


class IGsmModule(ABC):

    @abstractmethod
    def gsm_send_message(self, gsm_num, recipient, message):
        """
        This method is used to send a message using the GSM module
        :param: gsm_num: Number of the module as per configuration file key "deviceNumber"
        :param: recipient: Is the number for the recipient (send message on this number)
        :param: message: Message to be send
        :return: None
        """
        pass

    @abstractmethod
    def gsm_make_call(self, gsm_num, recipient):
        """
        This method is used to make the call using GSM modules
        :param: gsm_num: Number of the module as per configuration file key "deviceNumber"
        :param: recipient: Is the number for the recipient (make call on this number)
        :return: None
        """
        pass

    @abstractmethod
    def gsm_end_call(self, gsm_num):
        """
        This method is used to end the active call using GSM Module
        :param: gsm_num: Number of the module as per configuration file key "deviceNumber"
        :return: None
        """
        pass

    @abstractmethod
    def gsm_answer_call(self, gsm_num):
        """
        This method is used to answer the call using GSM module
        :param: gsm_num: Number of the module as per configuration file key "deviceNumber"
        :return: None
        """
        pass

    @abstractmethod
    def gsm_reject_call(self, gsm_num):
        """
        This method is used to reject the call using GSM Module
        :param: gsm_num: Number of the module as per configuration file key "deviceNumber"
        :return: None
        """
        pass
