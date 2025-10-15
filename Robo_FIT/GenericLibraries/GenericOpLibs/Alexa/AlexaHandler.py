import shutil

from Robo_FIT.GenericLibraries.GenericOpLibs.Alexa.AlexaExcelParser import AlexaExcelParser
from Robo_FIT.GenericLibraries.GenericOpLibs.Alexa.SpeechTextHandler import SpeechTextHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME
from diff_match_patch import diff_match_patch


class AlexaHandler:
    """
        This class is responsible for handling Alexa operations.
    """

    __ALEXA_INPUT_PATH = None
    VOLUME_LEVEL_HIGH = -0.0  # max value (100)
    VOLUME_LEVEL_LOW = -60  # min value (1)
    VOLUME_LEVEL_MEDIUM = -5.0  # medium value (72)

    def __init__(self, input_file_name="alexa_commands"):
        """
        Constructor of AlexaHandler
        The IAudioEndpointVolume interface represents the volume controls on the audio stream to
        or from an audio endpoint device Audio applications that use the MMDevice API and WASAPI typically use the
        ISimpleAudioVolume interface to manage stream volume levels on a per-session basis.
        :param input_file_name:alexa_commands.xlsx
        """
        try:
            robot_print_debug(f"Initialize {__class__} start")
            self.common_keywords = CommonKeywordsClass()
            self.output_cmd_dir_path = self.common_keywords.get_alexa_output_command_dir_path()
            self.alexa_excel = AlexaExcelParser(ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME)
            self.copy_the_excel_in_test_report(input_file_name)
            self.input_alexa_folder = AlexaHandler.__ALEXA_INPUT_PATH
            robot_print_debug("Input Alexa folder object Created!!")
            self.speech_text = SpeechTextHandler()
        except Exception as exp:
            robot_print_error(f"Error in AlexaHandler Class Constructor EXCEPTION:{exp}")

    def __get_input_alexa_path(self, input_file_name: str) -> str:
        """
        The method will give the alexa input path
        :param input_file_name: alexa_commands.xlsx
        :return: AlexaHandler.__ALEXA_INPUT_PATH
        """
        if AlexaHandler.__ALEXA_INPUT_PATH is None:
            AlexaHandler.__ALEXA_INPUT_PATH = os.path.join(self.common_keywords.get_alexa_report_path(),
                                                           self.__get_input_file_name(input_file_name))
            if not os.path.isfile(AlexaHandler.__ALEXA_INPUT_PATH):
                raise FileNotFoundError("Alexa folder is not found, Please create a folder before executing Alexa "
                                        "scripts.")
        return AlexaHandler.__ALEXA_INPUT_PATH

    def __get_input_file_name(self, input_file_name: str):
        return input_file_name if input_file_name.endswith(".xlsx") else f"{input_file_name}.xlsx"

    def send_alexa_command(self, unique_key, volume_level=VOLUME_LEVEL_HIGH):
        """
        The method will send the alexa command.
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc. command to be searched should be in above example format only
        :param volume_level :
        VOLUME_LEVEL_HIGH = -0.0  # max value (100)
        VOLUME_LEVEL_LOW = -60  # min value (1)
        VOLUME_LEVEL_MEDIUM = -5.0  # medium value (72)
        :return:Bool
        """
        try:
            # Is input Command and Expected Command not empty
            input_value = self.alexa_excel._get_input_cell_excel_data(unique_key)
            robot_print_info(f"Input command column cell value in alexa_commands.xlsx "
                             f"file is:{input_value}")
            output_value = self.alexa_excel._get_expected_cell_excel_data(unique_key)
            robot_print_info(f"Output command column cell value in alexa_commands.xlsx"
                             f" file is:{output_value}")
            if str(input_value) == "nan":
                robot_print_error(f"{input_value} from Input command column cell is Nan "
                                  f"in alexa_commands.xlsx file")
                return False

            elif str(output_value) == "nan":
                robot_print_error(
                    f"{output_value} from Output command column cell is "
                    f"Nan in alexa_commands.xlsx file")
                return False
            else:
                return self.speech_text.convert_text_to_speech(input_value,
                                                               self.common_keywords.get_alexa_report_input_command_path(
                                                                   unique_key), volume_level)
        except ValueError:
            robot_print_error(f"element to be searched in column not found in"
                              f" alexa_commands.xlsx file!!")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def __compute_similarity_and_diff(self, unique_key, threshold) -> bool:
        """
        Compare two blocks of plain text and efficiently return a list of differences.
        text1: Old string to be diffed.
        text2: New string to be diffed.
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG,
        :param threshold:need to set the value of threshold
        :return:Bool
        """
        try:
            output_column_value = self.alexa_excel._get_output_cell_excel_data(unique_key)
            robot_print_info("Output command column cell value in alexa_commands.xlsx file is :"
                             ":", output_column_value)

            expected_column_value = self.alexa_excel._get_expected_cell_excel_data(unique_key)
            robot_print_info("Expected command column cell value in alexa_commands.xlsx file "
                             "is :", expected_column_value)
            dmp = diff_match_patch()
            dmp.Diff_Timeout = 0.0
            diff = dmp.diff_main(output_column_value, expected_column_value, False)
            # similarity
            common_text = sum([len(txt) for op, txt in diff if op == 0])
            text_length = max(len(output_column_value), len(expected_column_value))
            similarity = common_text / text_length * 100
            conversion = float("{:.2f}".format(similarity))
            robot_print_info(f"conversion value is :{conversion}")
            if similarity >= threshold:
                robot_print_info(f"Similarity is: {similarity}")
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def compute_the_similarity_and_save_status(self, timeout: int, unique_key: str, threshold) -> bool:
        """
        The method will check if the given string is available or not in the output cell column and compare the cell values
        :param unique_key: command to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc.
             command to be searched should be in above example format only
        :param timeout : timeout  to listen
        :param threshold:need to set the value of threshold
        return :bool
        """
        try:
            input_text = self.speech_text.convert_speech_to_text(timeout, os.path.join(str(self.output_cmd_dir_path),
                                                                                       f"{unique_key}.mp3"))
            robot_print_info(f"Converted speech to text is:{input_text} ")
            self.alexa_excel._write_actual_output_to_cell_data(unique_key, input_text)
            output_string = self.__compute_similarity_and_diff(unique_key, threshold)
            robot_print_info(f"Output string is: {output_string}")
            if output_string is True:
                self.alexa_excel._write_status_to_cell_data(unique_key, "PASS")
                robot_print_info(f"PASS status value updated in status column "
                                 f"in alexa_commands.xlsx file", print_in_report=True)
                return True
            else:
                self.alexa_excel._write_status_to_cell_data(unique_key, "FAIL")
                robot_print_info(f"FAIL status value updated in status column"
                                 f" in alexa_commands.xlsx file", print_in_report=True)
                return False
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def copy_the_excel_in_test_report(self, input_file_name: str):
        """
        The method will copy the Excel in the test report like
        <CRE/SWE5_SWIntegrationTest/Test_Reports/Alexa/Reports/alexa_commands.xlsx>
        :param input_file_name: alexa_commands.xlsx
        """
        try:
            if os.path.isfile(os.path.join(
                    self.__get_input_file_name(input_file_name))):
                CommonKeywordsClass.TEST_MODULE_FOLDER = os.path.join(self.common_keywords.get_report_path(), "Alexa")
                if not os.path.isdir(CommonKeywordsClass.TEST_MODULE_FOLDER):
                    os.makedirs(CommonKeywordsClass.TEST_MODULE_FOLDER, mode=0o777, exist_ok=True)
                    robot_print_info(f"Created Module dir as:{CommonKeywordsClass.TEST_MODULE_FOLDER}")
                os.makedirs(
                    os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports"),
                    mode=0o777,
                    exist_ok=True)
                try:
                    input_file = self.alexa_excel.input_file_path
                    file = os.path.join(
                        os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports", "alexa_commands.xlsx"))
                    robot_print_info(file)
                    if os.path.isfile(file):
                        robot_print_info("file is already present")
                        return True
                    else:
                        shutil.copyfile(input_file, os.path.join(
                            os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports", "alexa_commands.xlsx")))
                except IOError as exp:
                    raise f"Unable to copy file:{exp}"
        except FileNotFoundError as file_exp:
            robot_print_info(f"Error to find the file, EXCEPTION: {file_exp}")
        except Exception as exp:
            robot_print_info("EXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}", print_in_report=True)

    def play_audio_file_from_input_directory(self, audio_file: str, volume_level: float):
        """
         Play the input Audio file
         :param audio_file:  name
         :param volume_level :
          VOLUME_LEVEL_HIGH = -0.0  # max value (100)
          VOLUME_LEVEL_LOW = -60  # min value (1)
          VOLUME_LEVEL_MEDIUM = -5.0  # medium value (72)
        """
        try:
            status = self.check_audio_file_in_directory(audio_file)
            robot_print_info(status)
            self.speech_text.play_audio_file(status, volume_level)
        except FileNotFoundError as file_exp:
            robot_print_info(f"Error to find the file, EXCEPTION: {file_exp}")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def check_audio_file_in_directory(self, audio_file: str) -> str | bool:
        """
        The method will check the input audio file in CRE/Libraries/ExternalFiles/InputFiles/Alexa directory.
        :param audio_file:audio file name
        :return:str | bool
        """
        try:
            list_of_files = os.listdir(self.input_alexa_folder)
            robot_print_info(f"The files in the alexa directory are:{list_of_files}", print_in_report=True)
            for file in os.listdir(self.input_alexa_folder):
                contains_path = os.path.join(self.input_alexa_folder, file)
                robot_print_info(f"path is:{contains_path}")
                if audio_file in str(list_of_files):
                    robot_print_info("file is available")
                    command_audio_path = os.path.join(self.input_alexa_folder, audio_file)
                    return command_audio_path
                else:
                    robot_print_info("file not available")
                    return False
        except FileNotFoundError as file_exp:
            robot_print_info(f"Error to find the file, EXCEPTION: {file_exp}")
        except FileExistsError as exp:
            robot_print_error(f" EXCEPTION : {exp}")
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def perform_alexa_operation(self, unique_key, timeout, threshold) -> bool:
        """

        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc. command to be searched should be in above example format only
        :param timeout : timeout  to listen
        :param threshold:
        :return:True/False
        """
        try:
            status = self.send_alexa_command(unique_key)
            robot_print_info(status)
            if status is True:
                output = self.compute_the_similarity_and_save_status(timeout, unique_key, threshold)
                # print(output)
                if output is True:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")
