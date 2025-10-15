import os
import sys
from datetime import datetime
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug


class ValidateResponse:
    __comparison_result = []

    def __compare_dict(self, expected_dict: dict, cloud_dict: dict):
        try:
            result = []
            for ex_key, ex_value in expected_dict.items():
                print(f"Expected: {expected_dict}, cloud: {cloud_dict}")
                if ex_key in cloud_dict.keys():
                    print(f"Type of Cloud {ex_key}: {type(cloud_dict[ex_key])} and expected {ex_key}: {type(ex_value)}")
                    if cloud_dict[ex_key] == ex_value:
                        print(
                            f"If side Type of Cloud {ex_key}: {cloud_dict[ex_key]} and expected {ex_key}: {ex_value}")
                        result.append(1)
                    else:
                        print(
                            f"Else side Type of Cloud {ex_key}: {cloud_dict[ex_key]} and expected {ex_key}: {ex_value}")
                        result.append(0)
                else:
                    result.append(0)
            if 0 in result:
                return 0
            elif 1 in result:
                return 1
        except Exception as exp:
            robot_print_error(f"Error to compare the expected and cloud response, "
                              f"\nExpected Output: {expected_dict}"
                              f"\nCloud Output: {cloud_dict}"
                              f"EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)

    def validate_response(self, vin_number: str, din_number: str, expected_output: dict, cloud_output: dict):
        """
        This method is used to validate the cloud response
        :param vin_number: VIN Number of HW
        :param din_number: DIN number of HW
        :param expected_output: Output to be expected
        :param cloud_output: Input comes from cloud
        """
        try:
            result = []
            cloud_vin_number = str(cloud_output["vin"])
            cloud_din_number = str(cloud_output["din"])
            expected_output["vin"] = vin_number
            expected_output["din"] = din_number
            if vin_number == cloud_vin_number and din_number == cloud_din_number:
                for expect_key, expect_value in expected_output.items():
                    if expect_key in cloud_output:
                        # check for timeStamp and ignore its "VALUE" for validation
                        if expect_key == "timeStamp":
                            # set the result true because timestamp is there.
                            result.append(1)
                        elif expect_key == "gnssInfo":
                            continue
                        else:
                            # check if cloud response for particular KEY is JSON
                            if isinstance(cloud_output[expect_key], dict):
                                result.append(
                                    self.__compare_dict(expected_output[expect_key], cloud_output[expect_key]))
                            # check if cloud response for particular KEY is LIST
                            elif isinstance(cloud_output[expect_key], list):
                                if expected_output[expect_key] == cloud_output[expect_key]:
                                    print(
                                        f"output Type is LIST verified with append 1, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{cloud_output[expect_key]}, "
                                        f"type of expected output is : {expected_output[expect_key]}")
                                    # if value same set flag True
                                    result.append(1)
                                else:
                                    print(
                                        f"output Type is LIST not verified with append 0, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{cloud_output[expect_key]}, "
                                        f"type of expected output is : {expected_output[expect_key]}")
                                    ValidateResponse.__comparison_result.append({expect_key: cloud_output[expect_key]})
                                    # and set a Flag False
                                    result.append(0)
                            elif isinstance(cloud_output[expect_key], str):
                                if expected_output[expect_key] == cloud_output[expect_key]:
                                    print(
                                        f"output Type is STR verified with append 1, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{cloud_output[expect_key]}, "
                                        f"type of expected output is : {expected_output[expect_key]}")
                                    result.append(1)
                                else:
                                    print(
                                        f"output Type is STR not verified with append 0, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{type(cloud_output[expect_key])}, "
                                        f"type of expected output is : {type(expected_output[expect_key])}")
                                    result.append(0)
                            elif isinstance(cloud_output[expect_key], int):
                                if expected_output[expect_key] == cloud_output[expect_key]:
                                    print(
                                        f"output Type is INT verified with append 1, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{cloud_output[expect_key]}, "
                                        f"type of expected output is : {expected_output[expect_key]}")
                                    result.append(1)
                                else:
                                    print(
                                        f"output Type is INT not verified with append 0, for key: {expect_key}, cloud output is : {cloud_output[expect_key]},"
                                        f" expected output is: {expected_output[expect_key]}, type of cloud output is :{cloud_output[expect_key]}, "
                                        f"type of expected output is : {expected_output[expect_key]}")
                                    result.append(0)
            else:
                robot_print_error(f"It seems either VIN or DIN number not as expected. "
                                  f"Please check logs. "
                                  f"\nExpected VIN number: {vin_number}, DIN Number: {din_number}"
                                  f"\nCloud VIN Number: {cloud_vin_number}, DIN Number: {cloud_din_number}",
                                  print_in_report=True)
                result.append(0)
            # Check the result
            if 0 in result:
                # If any 0 find in result list means some/all the expected key not match
                # the return False
                robot_print_error("Fail result : %s" % str(result), print_in_report=True)
                robot_print_error(ValidateResponse.__comparison_result, print_in_report=True)
                return False
            elif 1 in result:
                # If nay 1 find in the result list means all the expected key match
                # then return True
                robot_print_info("Pass result : %s " % str(result), print_in_report=True)
                robot_print_info(ValidateResponse.__comparison_result, print_in_report=True)
                return True

        except Exception as exp:
            robot_print_error(f"Error to validate the Broker response, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)

    def __write_payload_to_file(self, vin_num: str, din_num: str, cloud_output: dict, file_path: str,
                                itr_num: int = -1):
        try:
            with open(file_path, "a") as fp:
                time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if itr_num != -1:
                    fp.writelines(f"ITERATION NUMBER: {itr_num}\n")
                fp.writelines(f"TIME: {time}\n")
                fp.writelines(f"VIN NUMBER: {vin_num}\n")
                fp.writelines(f"DIN NUMBER: {din_num}\n")
                fp.writelines(f"MESSAGE: {str(cloud_output)}\n\n\n\n")
                fp.close()
        except FileNotFoundError as file_err:
            robot_print_error(f"the given file path '{file_path}' is not found, EXCEPTION: {file_err}",
                              print_in_report=True)
        except OSError as os_err:
            robot_print_error(f"Error to write the payload to file '{file_path}', EXCEPTION: {os_err}",
                              print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to write the payload to file '{file_path}', EXCEPTION: {exp}",
                              print_in_report=True)

    def validate_hygiene_payload(self, vin_num: str, din_num: str, expected_payload: dict, cloud_output: dict,
                                 write_to_file: bool = False, file_path=None, itr_num: int = -1):
        try:
            result = []
            cloud_vin_number = str(cloud_output["vin"])
            cloud_din_number = str(cloud_output["din"])
            if vin_num == cloud_vin_number and din_num == cloud_din_number:
                for expt_key in expected_payload.keys():
                    if expt_key in cloud_output.keys():
                        if isinstance(expected_payload[expt_key], dict) and isinstance(cloud_output[expt_key], dict):
                            for key in expected_payload[expt_key].keys():
                                if key in cloud_output[expt_key].keys():
                                    result.append(1)
                                else:
                                    robot_print_error(f"The expected key \"{key}\" is not in cloud response",
                                                      print_in_report=True)
                                    result.append(0)
                        result.append(1)
                    else:
                        robot_print_error(f"The expected key \"{expt_key}\" is not in cloud response",
                                          print_in_report=True)
                        result.append(0)

                if write_to_file and file_path is not None:
                    self.__write_payload_to_file(vin_num=vin_num, din_num=din_num, cloud_output=cloud_output,
                                                 file_path=file_path, itr_num=itr_num)

            if 0 in result:
                robot_print_error("For Hygiene payload result FAIL : %s " % str(result), print_in_report=True)
                robot_print_error(ValidateResponse.__comparison_result, print_in_report=True)
                return False
            if 1 in result:
                robot_print_info("For Hygiene payload result PASS : %s " % str(result), print_in_report=True)
                robot_print_info(ValidateResponse.__comparison_result, print_in_report=True)
                return True
        except Exception as exp:
            robot_print_error(f"Error to validate the Hygiene payload, EXCEPTION: {exp}", print_in_report=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)
