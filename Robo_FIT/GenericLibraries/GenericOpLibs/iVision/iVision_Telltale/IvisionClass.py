import requests
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Telltale.ConfigurationManager import ConfigurationManager

class IvisionClass:
    def __init__(self, url):
        """Initialize the IvisionClass with a server URL."""
        self.url = url
        self.config_manager = ConfigurationManager()
        self.oem = self.config_manager.get_oem()
        # self.oem = "GM"

    def get_response_server(self, file_path, filter_threshold=90, oem="GM"):
        """Send a POST request to the server with the provided file and thresholds."""
        headers = {'accept': 'application/json'}
        data = {
            'filter_threshold': str(filter_threshold),
            'oem': self.oem
        }
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.jpg' or file_extension == '.jpeg':
            mime_type = 'image/jpeg'
        elif file_extension == '.png':
            mime_type = 'image/png'
        else:
            raise ValueError("Unsupported image format. Only PNG and JPG are supported.")
        try:
            with open(file_path, 'rb') as file:
                files = {'image': (os.path.basename(file_path), file, mime_type)}
                response = requests.post(self.url, headers=headers, data=data, files=files)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    return response.text
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while sending the request: {e}")