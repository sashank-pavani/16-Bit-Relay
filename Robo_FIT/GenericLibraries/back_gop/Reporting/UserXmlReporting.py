from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.CreateXmlReport import CreateXmlReport


class UserXmlReporting:

    def __init__(self):
        self.xml_report = CreateXmlReport.get_xml_reporting_instance()

    def get_execution_start_time(self):
        self.xml_report.get_execution_start_time()

    def get_execution_end_time(self):
        self.xml_report.get_execution_end_time()

    def read_build_info(self, build_info):
        self.xml_report.read_build_info(build_info)

    def xml_create_root(self):
        self.xml_report.xml_create_root()

    def xml_add_module_name(self, module_name):
        self.xml_report.xml_add_module_name(module_name)

    def xml_add_suit_name(self, suit_name):
        self.xml_report.xml_add_suit_name(suit_name)

    def xml_add_adb_test_cases_data(self, test_case_name, start_time, end_time, status):
        self.xml_report.xml_add_adb_test_cases_data(test_case_name, start_time, end_time, status)

    def xml_add_adb_test_cases_screenshot(self, image_path):
        self.xml_report.xml_add_adb_test_cases_screenshot(image_path=image_path)

    def xml_add_test_case_start_time(self):
        self.xml_report.xml_add_test_start_time()

    def xml_add_test_case(self, test_case_name, status):
        self.xml_report.xml_add_test_case(test_case_name=test_case_name, status=status)

    def xml_add_ignition_data(self, test_case_name, start_time, log_file_name):
        self.xml_report.xml_add_ignition_data(test_case_name, start_time, log_file_name)

    def xml_create_serial_tag(self):
        self.xml_report.xml_create_serial_tag()

    def xml_add_crash_logs(self, file_name):
        self.xml_report.xml_add_crash_logs(file_name)

    def xml_add_can_trace(self, file_name):
        self.xml_report.xml_add_can_trace(file_name)

    def xml_add_serial_logs(self, logs_type, file_name):
        self.xml_report.xml_add_serial_logs(logs_type, file_name)

    def xml_add_suite_vst_logs(self, vst_logs_name):
        self.xml_report.xml_add_suite_vst_logs(vst_logs_name)

    def xml_add_adb_test_cases_vst_log(self, test_case_name, logfile_path):
        self.xml_report.xml_add_adb_test_cases_vst_log(test_case_name=test_case_name, logfile_path=logfile_path)

    def create_xml_file(self):
        self.xml_report.create_xml_file()

    def xml_add_crash_data(self, test_case_name, package_list: list):
        self.xml_report.xml_add_crash_data(test_case_name, package_list)

    def parse_xml_to_html(self):
        self.xml_report.parse_xml_to_html()


