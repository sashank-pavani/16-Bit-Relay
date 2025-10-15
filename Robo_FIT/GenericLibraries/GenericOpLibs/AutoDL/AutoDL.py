# import pyautogui
import time
import os
import requests
# import jenkinsapi
# from jenkinsapi.jenkins import Jenkins
import os
# import webbrowser
import glob
import shutil
# from zipfile import ZipFile
# from zipfile import BadZipfile
# import subprocess
# import time
from Robo_FIT.GenericLibraries.GenericOpLibs.AutoDL.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info
# import py7zr
import paramiko
from scp import SCPClient
# import serial
# import time
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.vAutoKit import *
import win32com.client


class AutoDL:

    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.DailyBuildJob = self.config_manager.get_job_name()
        self.Jenkins_Server = self.config_manager.get_jenkins_server()
        self.username = self.config_manager.get_jenkins_user()
        self.api_token = self.config_manager.get_jenkins_token()
        self.pending_stage = self.config_manager.get_pending_stage()
        self.ssh_host = self.config_manager.get_ssh_host()
        self.ssh_username = self.config_manager.get_ssh_username()
        self.ssh_password = self.config_manager.get_ssh_password()
        self.server_folder = self.config_manager.get_server_folder()
        # self.server_folder = '//chennai_cluster_gp/Hyundai_SU2IPE_EP30644/Hyundai_SU2IPE_Daily/programs/hyundai/my2024/su2ipe/out/IMG/SU2IPE_RUN1/release/SU2IPE_IMG_RUN1/images/USB_PKG'
        self.local_destination = self.config_manager.get_local_destination()
        self.mounteddrive = self.config_manager.get_Mounted_Drive()
        self.uuu_toolpath = self.config_manager.get_uuu_toolpath()
        self.nfs_shared_folder = self.config_manager.get_nfs_shared_folder()
        self.reportpath = self.config_manager.get_reportpath()
        self.jenkinsws = self.config_manager.get_jenkins_workspace()

    def ssh_connect_copy_server_build_binfiles1(self):

        ssh = ''
        try:
            # Establish an SSH connection
            # .SSHClient().close()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            robot_print_debug(f'scp init')
            ssh.connect(self.ssh_host, 22, self.ssh_username, self.ssh_password, timeout=600)
            shutil.rmtree(self.local_destination)
            # shutil.rmtree(self.local_destination + '\\USB_PKG')
            robot_print_debug(f'scp connected')
            # Initialize the SCPClient
            with SCPClient(ssh.get_transport()) as scp:
                # Copy files from the remote folder to the local folder
                robot_print_debug(f'copying bin files')
                scp.get(self.server_folder, self.local_destination, recursive=True)

            robot_print_debug(f'Files copied from {self.server_folder} to {self.local_destination}')
        except Exception as e:
            # robot_print_debug(f'Exception :{Exception}')
            robot_print_debug(f'SSH error: {e}')
            # pass

        finally:
            ssh.close()
    def ssh_connect_copy_server_build_binfiles(self, location):

        ssh = ''
        try:
            # Establish an SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            robot_print_info(f'scp init')
            ssh.connect(self.ssh_host, 22, self.ssh_username, self.ssh_password, timeout=600)
            shutil.rmtree(self.local_destination)
            robot_print_info(f'scp connected')
            # Initialize the SCPClient
            with SCPClient(ssh.get_transport()) as scp:
                # Copy files from the remote folder to the local folder
                robot_print_info(f'copying bin files')
                scp.get(location, self.local_destination, recursive=True)
            robot_print_info(f'Files copied from {location} to {self.local_destination}')
            return True
        except Exception as e:
            robot_print_error(f'SSH error: {e}')
            return False
        finally:
            ssh.close()

    def ssh_connect_copy_server_build_binfiles1(self):
        ssh = None
        try:
            # Establish an SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            robot_print_debug(f'SCP initialization')
            ssh.connect(self.ssh_host, 22, self.ssh_username, self.ssh_password, timeout=600)
            shutil.rmtree(self.local_destination)
            robot_print_debug(f'SCP connected')
            # Initialize SCP Client
            with SCPClient(ssh.get_transport()) as scp:
                robot_print_debug(f'Copying bin files from {self.server_folder} to {self.local_destination}')
                # Define a custom callback to print each file being copied
                def progress(filename):
                    robot_print_debug(f'Copying file: {filename}')
                # Copy files from the remote folder to the local folder
                scp.get(self.server_folder, self.local_destination, recursive=True, preserve_times=True,
                        progress=progress)
            robot_print_debug(f'Files copied from {self.server_folder} to {self.local_destination}')
        except Exception as e:
            robot_print_debug(f'SSH error: {e}')
        finally:
            if ssh:
                ssh.close()


    def get_build_number(self):
        api_url = f'{self.Jenkins_Server}/job/{self.DailyBuildJob}/lastBuild/buildNumber'

        try:
            response = requests.get(api_url, auth=(self.username, self.api_token))

            if response.status_code == 200:
                ongoing_build_number = int(response.text)
                robot_print_debug(f"Ongoing build number::{ongoing_build_number}")
                return ongoing_build_number
            else:
                robot_print_debug(f'Failed to retrieve build number. Status code: {response.status_code}')
        except Exception as e:
            robot_print_debug(f'An error occurred: {str(e)}')

    def get_latest_build_with_pending_stage(self):
        # API URL to get the latest build information
        api_url = f'{self.Jenkins_Server}/job/{self.DailyBuildJob}/lastBuild/api/json'

        # Create a session for HTTP requests and login
        session = requests.Session()
        session.auth = (self.username, self.api_token)
        time.sleep(5)
        try:
            while True:
                # Get the current build information
                response = session.get(api_url)
                response.raise_for_status()
                build_info = response.json()
                # Check if the build is in progress
                if build_info['building']:
                    # Get the build number and timestamp
                    build_number = build_info['number']
                    timestamp = build_info['timestamp']
                    displayName = build_info['displayName']
                    robot_print_debug(f"build number::{build_number}")
                    # print(build_number, build_info)
                    # Calculate the duration of the build in seconds
                    duration = int(time.time() * 1000) - timestamp

                    # API URL to get the current build's stage information
                    build_stage_url = f'{self.Jenkins_Server}/job/{self.DailyBuildJob}/{build_number}/wfapi/describe'
                    response = session.get(build_stage_url)
                    response.raise_for_status()
                    build_stage_info = response.json()
                    pending_stage = None
                    for stage in build_stage_info.get('stages', []):
                        if stage['status'] == 'PAUSED_PENDING_INPUT':
                            pending_stage = stage
                            break

                    if pending_stage:
                        pending_stage_name = pending_stage['name']
                        # robot_print_debug(f"build number::{build_number}")
                        robot_print_debug(f'Build #{build_number} is in progress:')
                        robot_print_debug(f' - Pending for Input: {pending_stage_name}\n')
                        if pending_stage_name == self.pending_stage:
                            return build_number
                        else:
                            robot_print_debug(
                                f'Build #{build_number} is in progress, but no pending stage is not {pending_stage} .')

                # Wait for a while before checking again (e.g., every minute)
                time.sleep(60)

        except requests.exceptions.RequestException as e:
            robot_print_debug(f'Error: {e}')

        finally:
            session.close()

    def Flash_Runcmd(self):
        IMAGE_PATH = self.local_destination + '\\USB_PKG'
        DEST_PATH = self.mounteddrive
        cmd = "cmd /c {0} {1}\\container-set-reflash.bin".format(self.uuu_toolpath, IMAGE_PATH)
        os.system(cmd)
        time.sleep(3)
        cmd = "cmd /c XCOPY {0}\\container-set-primary.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\container-set-reflash.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\ifs-primary.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\ifs-recovery.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\ifs-swupd.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\metadata.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\qnx6fs-app-partition.tar.gz {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\qnx6fs-asset-partition.tar.gz {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\qnx6fs-system-partition.tar.gz {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)
        cmd = "cmd /c XCOPY {0}\\m4-appl-container-su2ipe_run1.bin {1}".format(IMAGE_PATH, DEST_PATH)
        os.system(cmd)

    def check_screen_current(self):
        return True

    def qnx_image_capture(self):
        """
        This method takes the screenshot from QNX console and returns the path of the saved Image

        """
        try:
            count = 0
            dir_path = self.nfs_shared_folder
            robot_print_info(f"{dir_path}")
            #### from here
            for path in os.scandir(dir_path):
                if path.is_file():
                    count += 1
            robot_print_debug('file count:', count)
            file_name = 'screenshot'
            new_filename = file_name + "_" + str(count) + ".png"
            robot_print_debug(f"{new_filename}")

            # command5 = "/system/bin/screenshot -file=/share/{} -display=1\n".format(new_filename)

            # self.serial_cmd(command5)
            ###till here
            final_path = os.path.join(dir_path, new_filename)
            robot_print_info(f"final screenshot path---------{final_path}")
            return new_filename, final_path

        except Exception as e:
            robot_print_error(f"Unable to capture the Image please verify the configuration for Arduino :{e}")

    def delete_nfs_share(self):
        # Loop through files in the folder
        for file_name in os.listdir(self.nfs_shared_folder):
            # Check if the file is a .txt file
            if file_name.endswith('.png'):
                # Construct the full path to the file
                file_path = os.path.join(self.nfs_shared_folder, file_name)
                robot_print_debug(f'file_path #{file_path}deleted')
                # Remove the file
                os.remove(file_path)

    def copy_latest_2nd_3rd_folders(self):
        # Specify the directory where you want to find the latest folders
        directory = self.reportpath

        # List all subdirectories in the specified directory
        subdirectories = glob.glob(os.path.join(directory, '*'))

        # Sort the subdirectories by modification time (newest first)
        subdirectories.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Get the latest folder (index 0) and the second latest folder (index 1)
        latest_folder = subdirectories[0] if subdirectories else None
        second_latest_folder = subdirectories[1] if len(subdirectories) > 1 else None
        third_latest_folder = subdirectories[2] if len(subdirectories) > 2 else None
        print("Second Latest Folder:", second_latest_folder)
        print("Third Latest Folder:", third_latest_folder)

        if second_latest_folder:
            shutil.make_archive(os.path.join(self.jenkinsws, 'SanityReport'), 'zip', second_latest_folder)
            print(f"Folder {second_latest_folder} has been zipped as 'SanityReport.zip'.")

        if third_latest_folder:
            shutil.make_archive(os.path.join(self.jenkinsws, 'AutoFlashReport'), 'zip', third_latest_folder)
            print(f"Folder {third_latest_folder} has been zipped as 'AutoFlashReport.zip'.")


if __name__ == '__main__':
    pass
    # h = AutoDL()
    # h.get_latest_build_with_pending_stage(Jenkins_Server, DailyBuildJob, username, api_token, pending_stage)
    # h.ssh_connect_copy_server_build_binfiles(ssh_host, ssh_port, ssh_username, ssh_password, server_folder, local_destination)
    # h.flash_mode(mode, ign, bat)
    # h.Flash(Bat_File_Path, Bat_File1, Bat_File2, teraterm_port)
    # h.power_mode(mode, ign, bat)
    # # h.check_screen_current()


