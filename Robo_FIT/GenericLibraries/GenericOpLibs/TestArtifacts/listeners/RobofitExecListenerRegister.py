from typing import List

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.listeners.RobofitExecListener import RobofitExecListener


class RobofitExecListenerRegister:
    __listener: List[RobofitExecListener] = []

    @staticmethod
    def get_listeners() -> List[RobofitExecListener]:
        if RobofitExecListenerRegister.__listener is not None:
            return RobofitExecListenerRegister.__listener
        robot_print_debug("No listeners are registered")

    @staticmethod
    def register_listener(listener: RobofitExecListener):
        RobofitExecListenerRegister.__listener.append(listener)

    @staticmethod
    def deregister_listener(listener: RobofitExecListener):
        RobofitExecListenerRegister.__listener.remove(listener)
