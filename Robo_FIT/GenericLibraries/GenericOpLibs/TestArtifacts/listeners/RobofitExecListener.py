from abc import ABCMeta, abstractmethod


class RobofitExecListener(metaclass=ABCMeta):
    """
    Abstract base class for creating custom listeners that can react to Robot Framework execution events.
    """

    def on_execution_start(self):
        """
        This method is called when the execution starts.
        """
        pass

    @abstractmethod
    def on_execution_complete(self):
        """
        This method is called when the execution is complete.
        """
        pass

    @abstractmethod
    def on_test_start(self, test_case_data=None):
        """
        This method is called when a test starts.
        """
        pass

    @abstractmethod
    def on_test_end(self, test_data, test_result):
        """
        This method is called when a test ends.
        """
        pass
