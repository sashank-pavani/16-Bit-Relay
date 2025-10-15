import requests
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *

class IvisionClass:
    def __init__(self, url):
        """Initialize the IvisionClass with a server URL."""
        self.url = url

    def send_request(self, url, file_path, bw_threshold, ocr_output, interword_spaces, preprocessing_algorithm, psm,
                      lang, region, confidence_threshold, oem):
        """Helper method to send a POST request to the server with the provided file and thresholds."""
        data = {
            "bw_threshold": str(bw_threshold),
            "ocr_output": ocr_output,
            "interword_spaces": str(interword_spaces),
            "preprocessing_algorithm": preprocessing_algorithm,
            "psm": str(psm),
            "lang": lang,
            "region": region,
            "confidence_threshold": str(confidence_threshold),
            "oem": str(oem)
        }

        headers = {"accept": "application/json"}
        file_extension = os.path.splitext(file_path)[1].lower()
        mime_type = "image/jpeg" if file_extension in [".jpg", ".jpeg"] else "image/png"

        with open(file_path, "rb") as file:
            files = {"image": (os.path.basename(file_path), file, mime_type)}
            robot_print_debug(f"Sending POST Request: url={url}, data={data}, file={file_path}")
            try:
                response = requests.post(url, headers=headers, data=data, files=files)
                response.raise_for_status()
                return response
            except requests.HTTPError as e:
                robot_print_error(f"HTTP Error: {e}, Response: {e.response.text}")
                raise RuntimeError(f"HTTP Error: {e}, Response: {e.response.text}")
            except Exception as e:
                robot_print_error(f"Unexpected error occurred while sending request: {e}")
                raise RuntimeError(f"Unexpected error occurred while sending request: {e}")

