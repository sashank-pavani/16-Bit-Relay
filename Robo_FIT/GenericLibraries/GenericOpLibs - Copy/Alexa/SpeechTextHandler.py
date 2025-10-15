"""
pip install SpeechRecognition : Library for performing speech recognition, with support for
several engines and APIs.

pyttsx3 library is a text-to-speech conversion library in Python. It is a help to convert the entered text into speech.
"""
import errno

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ExcelParser import ExcelParser
import winsound
import aifc
import wave
import speech_recognition as sr
import pyttsx3
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME
import os.path


class SpeechTextHandler:
    """
    This class is used for translating the speech to text and text to speech. This is done with the help of Google
    Speech Recognition.

    """

    def __init__(self):
        """
        Constructor of SpeechTextHandler
        pyttsx3 library is a text-to-speech conversion library in Python
        It is a help to convert the entered text into speech.
        """
        try:
            robot_print_debug(f"Initialize {__class__} start")
            self.excel_parser = ExcelParser(ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME)
            self.engine = pyttsx3.init()
            # init function to get an engine instance for the speech synthesis
            self.recognizer = sr.Recognizer()
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def convert_speech_to_text(self, timeout: int, filename):
        """
        This method is used to covert the speech to text.
        Use the microphone as source for input and adjust the energy threshold based on the surrounding noise level
        listens for the user's input then using Google to recognize audio.
        :param timeout:  timeout to listen
        :param filename: filename where audio should be stored
        :return: input text
        """
        try:
            # use the microphone as source for input.
            with sr.Microphone() as source:
                # wait for a second to let the recognizer
                # adjust the energy threshold based on the surrounding noise level
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                robot_print_debug("Start to listen...")
                audio = self.recognizer.listen(source, timeout)
                print("Type of duration:", type(timeout))
                # self.recognizer.record(source, duration=60)
                # It will try to listen until the user does not speak for 60 seconds.
                robot_print_debug("listening timeout end here")
                with open(filename, "wb") as file:
                    file.write(audio.get_wav_data())
                # record the speech audio
                input_text = self.recognizer.recognize_google(audio)
                # Using google to recognize audio
                input_text = input_text.lower()
                robot_print_info(f"converted the volume to text is: {input_text}")
                return input_text
        except sr.RequestError as e:
            robot_print_debug("Could not request results; {0}".format(e))
        except sr.WaitTimeoutError:
            robot_print_error("time out")  # error handler for time out error
        except (sr.UnknownValueError, wave.Error, ValueError, aifc.Error, EOFError):
            robot_print_error("The audio file could not be read; check to see if it is corrupted.")
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def convert_text_to_speech(self, input_text: str, filename: str, volume_level: float):
        """
        The method will help with the conversion of text to speech.
        Initialize the Pyttsx3 engine.
        engine = pyttsx3.init()
        We can use file extension as mp3 and wav, both will work
        runAndWait:  Runs an event loop until all commands queued up until this method call
        complete.
        :param input_text:  user need to give alexa command
        :param filename: the name of file to save.
        :param volume_level:
        :return: Bool
        """
        try:

            self.engine.save_to_file(input_text, filename)
            self.engine.runAndWait()
            robot_print_debug(f"{'*' * 20}Playing Audio for {input_text}{'*' * 20}")
            return self.play_audio_file(filename, volume_level)
        except (sr.UnknownValueError, sr.WaitTimeoutError, sr.WaitTimeoutError) as Exp:
            robot_print_error("The audio file could not be read; check to see if it is corrupted.", Exp)
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def play_audio_file(self, filename: str, volume_level: float):
        """
        The win sound module provides access to the basic sound-playing machinery provided by Windows platforms. It
        includes functions and several constants. Call the underlying PlaySound() function from the Platform API. The
        sound parameter may be a filename, a system sound alias, audio data as a bytes-like object, or None.
        :param filename: audio path
        :param volume_level:
            HIGH_VALUE = -0.0  # max value (100)
            LOW_VALUE = -60  # min value (1)
            MEDIUM_VALUE = -5.0  # medium value (72)
        """
        try:
            # volume increase of system
            if os.path.isfile(filename):
                self.__volume_scenarios_for_system(volume_level)
                robot_print_info("Volume set to 100")
                winsound.PlaySound(filename, winsound.SND_FILENAME)
                return True
            else:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), filename)
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def __volume_scenarios_for_system(self, volume_level: float):
        """
        pycaw is Python Core Audio Windows Library
        The method will monitor the volume of system.
        :param volume_level:
            HIGH_VALUE = -0.0  # max value (100)
            LOW_VALUE = -60  # min value (1)
            MEDIUM_VALUE = -5.0  # medium value (72)
        :return: True if success
        """
        try:
            robot_print_info(f"Current system Volume is:", self.volume.GetMasterVolumeLevel())
            self.volume.SetMasterVolumeLevel(volume_level, None)
            robot_print_debug(f"Increase system Volume is:", self.volume.GetMasterVolumeLevel())
            return True
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")
