import sys

from dominate.tags import ul
from robot.api import logger
import os
import dominate
from datetime import datetime
from dominate.tags import *
from xml.etree import ElementTree
from lxml import etree
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_BUILD_INFO_FILE
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info, robot_print_error


class CreateXmlReport:
    __instance = None

    ROOT = None
    TAG_MODULE_NAME = None
    TAG_SUIT_NAME = None
    TAG_TEST_CASE = None
    TAG_TEST_CASE_LOG = None
    TAG_TEST_CASE_IMAGE = None
    TAG_IGN_NAME = None
    TAG_CRASH_INFO = None
    TAG_SERIAL_TAG = None
    TAG_CRASH_LOGS = None
    TAG_SERIAL_LOGS = None
    TAG_CAN_TRACE = None
    STR_MODULE_NAME = ""
    STR_SUIT_NAME = ""
    BUILD_INFO = ""
    EXC_START_TIME = ""
    EXC_END_TIME = ""
    TEST_START_TIME = None

    @staticmethod
    def get_xml_reporting_instance() -> 'CreateXmlReport':
        if CreateXmlReport.__instance is None:
            CreateXmlReport()
        return CreateXmlReport.__instance

    def __call__(self):
        robot_print_error(f"You can't create the object of CreateXmlReport() class, "
                          f"Please create the object of UserXmlReporting().",
                          print_in_report=True, underline=True)
        raise self

    def __init__(self):
        CreateXmlReport.__instance = self
        self.get_report_path = None
        self.get_crash_log_path = None
        self.custom_path = None
        CreateXmlReport.__instance = self

    def get_execution_start_time(self):
        CreateXmlReport.EXC_START_TIME = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    def __get_build_info(self):
        try:
            build_number = 0
            common_keywords = CommonKeywordsClass()
            with open(os.path.join(common_keywords.get_root_path(), PROJECT, CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES,CRE_BUILD_INFO_FILE)) as fp:
                build_number = fp.readline()
                fp.close()
            return build_number
        except Exception as exp:
            robot_print_error(f"Error to read the BuildInfo.txt file, EXCEPTION: {exp}")

    def get_execution_end_time(self):
        try:
            global EXC_END_TIME
            CreateXmlReport.EXC_END_TIME = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            etree.SubElement(CreateXmlReport.ROOT, "execinfo",
                             starttime=str(CreateXmlReport.EXC_START_TIME),
                             endtime=datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
                             buildinfo=self.__get_build_info())
        except Exception as exp:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exp)
            logger.console(exc_type, fname, exc_tb.tb_lineno)

    def read_build_info(self, build_info):
        CreateXmlReport.BUILD_INFO = str(build_info)

    def xml_create_root(self):
        self.get_execution_start_time()
        CreateXmlReport.ROOT = etree.Element("customreport")
        self.xml_create_serial_tag()

    def xml_add_module_name(self, module_name):
        CreateXmlReport.TAG_MODULE_NAME = etree.SubElement(CreateXmlReport.ROOT, "modulename", name=module_name)
        CreateXmlReport.STR_MODULE_NAME = module_name

    def xml_add_suit_name(self, suit_name):
        CreateXmlReport.TAG_SUIT_NAME = etree.SubElement(CreateXmlReport.TAG_MODULE_NAME, "suitname",
                                                         id=suit_name.split(".")[-1],
                                                         name=suit_name,
                                                         vst="",
                                                         nodeid="",
                                                         downloadlink="")
        CreateXmlReport.STR_SUIT_NAME = suit_name

    def xml_add_adb_test_cases_data(self, test_case_name, start_time, end_time, status):
        robot_print_info(f"CreateXmlReport.TAG_TEST_CASE_IMAGE: {CreateXmlReport.TAG_TEST_CASE_IMAGE}")
        robot_print_info(f"CreateXmlReport.TAG_TEST_CASE_LOG: {CreateXmlReport.TAG_TEST_CASE_LOG}")
        CreateXmlReport.TAG_TEST_CASE = etree.SubElement(CreateXmlReport.TAG_SUIT_NAME, "testcases",
                                                         id=test_case_name.split(" ")[0],
                                                         name=test_case_name,
                                                         starttime=start_time,
                                                         endtime=end_time,
                                                         status=status,
                                                         logdownlodlink="",
                                                         imagedownloadlink="",
                                                         vst="", nodeid="", vstdownloadlink="")

    def xml_add_adb_test_cases_vst_log(self, test_case_name, logfile_path):
        robot_print_info(f"CreateXmlReport.TAG_TEST_CASE.attrib['id']: {CreateXmlReport.TAG_TEST_CASE.attrib['id']}")
        if CreateXmlReport.TAG_TEST_CASE.attrib["id"] == test_case_name.split(" ")[0]:
            CreateXmlReport.TAG_TEST_CASE.attrib["vst"] = os.path.split(logfile_path)[1]

    def xml_add_adb_test_cases_screenshot(self, image_path):
        CreateXmlReport.TAG_TEST_CASE_IMAGE = os.path.split(image_path)[1]

    def xml_add_test_start_time(self):
        CreateXmlReport.TEST_START_TIME = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    def xml_add_test_case(self, test_case_name: str, status):
        test_case_name = test_case_name.split(" ")[0]
        CreateXmlReport.TAG_TEST_CASE = etree.SubElement(CreateXmlReport.TAG_SUIT_NAME, "tcases",
                                                         name=test_case_name,
                                                         starttime=CreateXmlReport.TEST_START_TIME,
                                                         endtime=datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
                                                         status=status)

    def xml_add_ignition_data(self, test_case_name, start_time, log_file_name):
        CreateXmlReport.TAG_IGN_NAME = etree.SubElement(CreateXmlReport.TAG_SUIT_NAME, "ignition",
                                                        name="IGN_%s" % test_case_name,
                                                        testcasename=test_case_name,
                                                        suitname=CreateXmlReport.STR_SUIT_NAME.split(".")[2],
                                                        modulename=CreateXmlReport.STR_MODULE_NAME,
                                                        time=start_time, logfilename=log_file_name)
        logger.console("IGN data set successfully. %s" % str(CreateXmlReport.TAG_IGN_NAME))

    def xml_create_serial_tag(self):
        CreateXmlReport.TAG_SERIAL_TAG = etree.SubElement(CreateXmlReport.ROOT, "seriallog")

    def xml_add_crash_logs(self, file_name):
        CreateXmlReport.TAG_CRASH_LOGS = etree.SubElement(CreateXmlReport.ROOT, "crashlog", filename=file_name,
                                                          nodeid="", downloadlink="")

    def xml_add_can_trace(self, file_name):
        CreateXmlReport.TAG_CAN_TRACE = etree.SubElement(CreateXmlReport.ROOT, "cantrace", filename=file_name,
                                                         nodeid="", downloadlink="")

    def xml_add_serial_logs(self, logs_type, file_name):
        CreateXmlReport.TAG_SERIAL_LOGS = etree.SubElement(CreateXmlReport.TAG_SERIAL_TAG, "logstype",
                                                           logstype=logs_type, filename=file_name,
                                                           nodeid="", downloadlink="")

    def xml_add_suite_vst_logs(self, vst_logs_name):
        try:
            CreateXmlReport.TAG_SUIT_NAME.attrib["vst"] = os.path.split(vst_logs_name)[1]
        except Exception as exp:
            robot_print_error(f"Error to add the VST logs link, EXCEPTION: {exp}")

    def create_xml_file(self):
        common_keywords = CommonKeywordsClass()
        self.get_report_path = common_keywords.get_report_path()
        self.get_crash_log_path = common_keywords.get_crash_log_path()
        if os.path.isdir(os.path.join(common_keywords.get_report_path(), "PerformanceUtilisation", "BootKpiValue")):
            self.custom_path = common_keywords.performance_utilization_custom_path("BootKpiValue")
        print("XML Path: %s" % self.get_report_path)
        logger.console("XML Path: %s" % self.get_report_path)
        save_file_at_path = os.path.join(self.get_report_path, "Custom.xml")
        logger.console("Xml file path is : ", save_file_at_path)
        file = open(save_file_at_path, "w")
        file.write(etree.tostring(CreateXmlReport.ROOT, pretty_print=True).decode('utf-8'))
        file.close()

    def xml_add_crash_data(self, test_case_name, package_list):
        CreateXmlReport.TAG_CRASH_INFO = etree.SubElement(CreateXmlReport.TAG_SUIT_NAME, "crashinfo",
                                                          name="CRASH_%s" % test_case_name,
                                                          testcasename=test_case_name,
                                                          suitname=CreateXmlReport.STR_SUIT_NAME,
                                                          modulename=CreateXmlReport.STR_MODULE_NAME,
                                                          packagelist=package_list)

    def parse_xml_to_html(self):
        try:
            logger.console("Collecting the data and start creating report...!!!")
            self.get_execution_end_time()
            total_test_pass = 0
            total_test_fail = 0
            # initialize the dominate
            doc = dominate.document("Automation Report")
            li_modules_links = li()
            # aad the head for HTML page
            with doc.head:
                link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css")
                script(type='text/javascript', src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js")
                script(type='text/javascript',
                       src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js")
            # start adding body of HTML page
            with doc:
                # add the <navbar></navbar> tag for the
                nav_bar = nav()
                nav_bar.set_attribute("class", "navbar navbar-inverse navbar-fixed-top")
                with nav_bar:
                    nav_div = div()
                    nav_div.set_attribute("class", "container-fluid")
                    with nav_div:
                        nav_div_two = div()
                        nav_div_two.set_attribute("class", "navbar-header")
                        with nav_div_two:
                            name = a("Automation Report", href="https://www.visteon.com/")
                            name.set_attribute("class", "navbar-brand")
                        ul_tag = ul()
                        ul_tag.set_attribute("class", "nav navbar-nav")
                        with ul_tag:
                            li_tag = li()
                            li_tag.set_attribute("class", "active dropdown")
                            with li_tag:
                                a_link = a("Modules List", href="#")
                                a_link.set_attribute("class", "dropdown-toggle")
                                a_link.set_attribute("data-toggle", "dropdown")
                                a_link.add_raw_string("<span class=\"caret\"></span>")
                                ul_drop_down = ul()
                                ul_drop_down.set_attribute("class", "dropdown-menu")
                                ul_drop_down.add(li_modules_links)
                            mem_li_tag = li()
                            mem_li_tag.set_attribute("class", "dropdown")
                            with mem_li_tag:
                                mem_a_link = a("Memory Reports", href="#")
                                mem_a_link.set_attribute("class", "dropdown-toggle")
                                mem_a_link.set_attribute("data-toggle", "dropdown")
                                mem_a_link.add_raw_string("<span class=\"caret\"></span>")
                                mem_ul_drop_down = ul()
                                mem_ul_drop_down.set_attribute("class", "dropdown-menu")
                                with mem_ul_drop_down:
                                    if os.path.isdir(os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                                  "Memory", "QnxMemory")):
                                        list_of_html = os.listdir(
                                            os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                         "Memory", "QnxMemory"))
                                        for file in list_of_html:
                                            if file.endswith(".html"):
                                                li(a(f"{file.split('.')[0]}",
                                                     href=f"./PerformanceUtilisation/Memory/QnxMemory/{file}",
                                                     target="_blank",
                                                     rel="noopener noreferrer"))
                                    if os.path.isdir(os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                                  "Memory", "AndroidMemory")):
                                        list_of_html = os.listdir(
                                            os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                         "Memory", "AndroidMemory"))
                                        for file in list_of_html:
                                            if file.endswith(".html"):
                                                li(a(f"{file.split('.')[0]}",
                                                     href=f"./PerformanceUtilisation/Memory/AndroidMemory/{file}",
                                                     target="_blank",
                                                     rel="noopener noreferrer"))
                                cpu_li_tag = li()
                                cpu_li_tag.set_attribute("class", "dropdown")
                                with cpu_li_tag:
                                    cpu_a_link = a("CPU Reports", href="#")
                                    cpu_a_link.set_attribute("class", "dropdown-toggle")
                                    cpu_a_link.set_attribute("data-toggle", "dropdown")
                                    cpu_a_link.add_raw_string("<span class=\"caret\"></span>")
                                    cpu_ul_drop_down = ul()
                                    cpu_ul_drop_down.set_attribute("class", "dropdown-menu")
                                    with cpu_ul_drop_down:
                                        if os.path.isdir(os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                                      "CPU", "QnxCpu")):
                                            list_of_html = os.listdir(
                                                os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                             "CPU", "QnxCpu"))
                                            for file in list_of_html:
                                                if file.endswith(".html"):
                                                    li(a(f"{file.split('.')[0]}",
                                                         href=f"./PerformanceUtilisation/CPU/QnxCpu/{file}",
                                                         target="_blank",
                                                         rel="noopener noreferrer"))
                                        if os.path.isdir(os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                                      "CPU", "AndroidCpu")):
                                            list_of_html = os.listdir(
                                                os.path.join(self.get_report_path, "PerformanceUtilisation",
                                                             "CPU", "AndroidCpu"))
                                            for file in list_of_html:
                                                if file.endswith(".html"):
                                                    li(a(f"{file.split('.')[0]}",
                                                         href=f"./PerformanceUtilisation/CPU/AndroidCpu/{file}",
                                                         target="_blank",
                                                         rel="noopener noreferrer"))
                                robot_li_tag = li(a("Robot Reports", href="./Reports/test_report.html", target="_blank",
                                                    rel="noopener noreferrer"))
                                if self.custom_path is not None:
                                    android_boot_kpi = li(a("Android Boot KPI Value",
                                                            href="./PerformanceUtilisation/BootKpiValue/boot_kpi.html",
                                                            target="_blank", rel="noopener noreferrer"))

                # add the alert for the INFO message
                div_canvas_info = div()
                div_canvas_info.add_raw_string("""
                <div class="alert alert-info alert-dismissible text-center" style="margin-top: 50px;">
                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
                <strong>Note!</strong><br />
                <span style="color: blue;">Blue Color indicate Module Name</span>  and   
                <span style="color: peru;">Peru Color indicate Suit Name</span>
                </div>""")

                # add the summary <div> tag to add the summary of the test cases
                summary_div = div()
                summary_div.set_attribute("class", "container")
                summary_div.set_attribute("style", "margin-top: 50px;")
                with summary_div:
                    test_report_heading = h1("Testcases Report")
                    test_report_heading['align'] = "center"
                    test_report_heading["style"] = "color: black;"
                    summary_heading = h3("Summary Information")
                    summary_heading["style"] = "color: slategray"
                    summary_info_div = div()
                    summary_info_div.set_attribute("class", "row well well-lg")

                # div of test report summary,
                # It contains the table of PASS And FAIL test cases
                div_test_summary = div()
                div_test_summary.set_attribute("class", "container")
                div_test_summary.set_attribute("style", "margin-top: 20px;")
                test_statistics_heading = h3("Test Statistics")
                test_statistics_heading['align'] = "left"
                test_statistics_heading["style"] = "color: slategray;"
                div_test_summary.add(test_statistics_heading)
                test_summary_table = table()
                test_summary_table.set_attribute("class",
                                                 "table table-striped table-bordered table-condensed table-hover")
                with test_summary_table.add(tbody()):
                    th("Name")
                    th("Total Cases")
                    th("Pass Cases")
                    th("Fail Cases")
                # start adding the module name and create the <div> tag for the
                module_name_div = div()
                module_name_div.set_attribute("class", "container")
                module_name_div.set_attribute("style", "margin-top:50px")
                module_name_div.set_attribute("id", "abc")
                with module_name_div:
                    # start iterating the ROOT of xml file and get the data
                    for module_name in CreateXmlReport.ROOT.iter("modulename"):
                        # set a variable to store the PASS and FAIL test cases record in module.
                        m_test_pass = 0
                        m_test_fail = 0
                        # add the row for add the module row in the summary <div> tag
                        tr_module_summary = tr()
                        tr_module_summary.set_attribute("style", "color: blue;")
                        tr_module_summary.add(
                            td(a(module_name.attrib["name"], href="#%s" % module_name.attrib["name"])))

                        # add the heading for the module name, show in blue color in report.
                        module_heading = h1(module_name.attrib["name"])
                        module_heading['style'] = 'color: blue'
                        module_heading['align'] = 'left'
                        module_heading['id'] = module_name.attrib["name"]
                        module_name_div.add(module_heading)

                        # start iterating the suit name for the xml file
                        for suitname in module_name.iter("suitname"):
                            # set the variable to store the PASS and FAIL cases in perticular suit
                            s_test_pass = 0
                            s_test_fail = 0

                            # get the name of the suit so that add it into the summary tag.
                            t_name = "{m}-{s}".format(m=module_name.attrib["name"],
                                                      s=suitname.attrib["name"].split(".")[2])
                            tr_suit_summary = tr()
                            tr_suit_summary.set_attribute("style", "color: peru;")
                            tr_suit_summary.add(td(a(t_name, href="#%s" % suitname.attrib["name"].split(".")[2])))

                            # add the link of the suit in the <li> tag of <navbar> tag
                            li_modules_links.add_raw_string(
                                "<a href=\"#{module_link}\">{modulename}-{suitname}</a>".format(
                                    module_link=suitname.attrib["name"].split(".")[2],
                                    modulename=module_name.attrib["name"],
                                    suitname=suitname.attrib["name"].split(".")[2]))

                            # add the suit name heading
                            suit_name_heading = h3(suitname.attrib["name"].split(".")[2])
                            suit_name_heading['style'] = 'color: peru'
                            suit_name_heading['align'] = 'left'
                            suit_name_heading['id'] = suitname.attrib["name"].split(".")[2]
                            module_name_div.add(suit_name_heading)

                            # div for test case ignition cases and crash cases logs
                            # which contains the links of that per suit
                            div_link_heading = div()
                            div_link_heading.set_attribute("class", "container row")
                            with div_link_heading:
                                # add test cases link inside module div tag
                                test_cases_link = a("Test Cases Logs", role="button",
                                                    href="#{test}{suit}".format(test="test",
                                                                                suit=suitname.attrib["name"].split(".")[
                                                                                    2]))
                                test_cases_link.set_attribute("class", "btn btn-info")
                                test_cases_link.set_attribute("align", "center")
                                test_cases_link.set_attribute("style", "width: ")
                                # add ignition link inside module div tag
                                ignition_link = a("Ignition Logs", role="button", href="#{ign}{suit}".format(ign="ign",
                                                                                                             suit=
                                                                                                             suitname.attrib[
                                                                                                                 "name"].split(
                                                                                                                 ".")[
                                                                                                                 2]))
                                ignition_link.set_attribute("class", "btn btn-info")
                                ignition_link.set_attribute("align", "center")
                                # add crash logs link inside module div tag
                                crash_logs_link = a("Crash Logs", href="#{crash}{suit}".format(crash="crash", suit=
                                suitname.attrib["name"].split(".")[2]))
                                crash_logs_link.set_attribute("class", "btn btn-info")
                                crash_logs_link.set_attribute("align", "center")

                            module_name_div.add(div_link_heading)
                            # create the table to add the test case name and their info
                            test_case_heading = h3("All Test Report")
                            test_case_heading['align'] = "center"
                            test_case_heading['style'] = "color: black;"
                            test_report_heading['id'] = "#{test}{suit}".format(test="test",
                                                                               suit=suitname.attrib["name"].split(".")[
                                                                                   2])
                            test_case_table = table()
                            test_case_table.set_attribute('class',
                                                          'table table-striped table-bordered table-condensed table-hover')
                            with test_case_table.add(tbody()):
                                th("Test Name")
                                th("Start Time (Target Time)")
                                th("End Time(Target Time)")
                                th("Status")
                                th("Log Files")
                                th("Image")
                                # iterating the testcases tag in xmal file and get info
                                for testcase in suitname.iter("testcases"):
                                    l = tr()
                                    l += td(testcase.attrib["name"])
                                    with l:
                                        td(testcase.attrib["starttime"])
                                        td(testcase.attrib["endtime"])
                                        status = testcase.attrib["status"]
                                        if status == "PASS":
                                            m_test_pass += 1
                                            s_test_pass += 1
                                            total_test_pass += 1
                                            pass_td = td(status)
                                            pass_td.set_attribute("style", "color: green")
                                            td("No Log..!!!")
                                            td("No Screenshot..!!!")
                                        elif status == "FAIL":
                                            m_test_fail += 1
                                            s_test_fail += 1
                                            total_test_fail += 1
                                            fail_td = td(status)
                                            fail_td.set_attribute("style", "color: red")
                                            log_file_path = os.path.join(module_name.attrib["name"], "Logs_Screenshot",
                                                                         testcase.attrib["name"].split(" ")[0],
                                                                         testcase.attrib["name"].split(" ")[0] + ".log")
                                            img_file_path = os.path.join(module_name.attrib["name"], "Logs_Screenshot",
                                                                         testcase.attrib["name"].split(" ")[0],
                                                                         testcase.attrib["name"].split(" ")[0] + ".png")
                                            td(a(testcase.attrib["name"].split(" ")[0], href="./%s" % log_file_path,
                                                 target="_blank",
                                                 rel="noopener noreferrer"))
                                            td(a(testcase.attrib["name"].split(" ")[0], href="./%s" % img_file_path,
                                                 target="_blank",
                                                 rel="noopener noreferrer"))
                            test_case_table2 = table()
                            test_case_table2.set_attribute('class',
                                                           'table table-striped table-bordered table-condensed table-hover')
                            with test_case_table2.add(tbody()):
                                th("Test Name")
                                th("Start Time (Host Time)")
                                th("End Time(Host Time)")
                                th("Status")
                                # iterating the testcases tag in xmal file and get info
                                for testcase in suitname.iter("tcases"):
                                    l = tr()
                                    l += td(testcase.attrib["name"])
                                    with l:
                                        td(testcase.attrib["starttime"])
                                        td(testcase.attrib["endtime"])
                                        status = testcase.attrib["status"]
                                        if status == "PASS":
                                            m_test_pass += 1
                                            s_test_pass += 1
                                            total_test_pass += 1
                                            pass_td = td(status)
                                            pass_td.set_attribute("style", "color: green")
                                        elif status == "FAIL":
                                            m_test_fail += 1
                                            s_test_fail += 1
                                            total_test_fail += 1
                                            fail_td = td(status)
                                            fail_td.set_attribute("style", "color: red")
                            module_name_div.add(test_case_heading)
                            module_name_div.add(test_case_table)
                            module_name_div.add(test_case_table2)
                            ignition = suitname.find('ignition')
                            if ignition is None:
                                # print no ignition log
                                ign_table = None
                                ign_heading = h5("No ignition happened in this suit...!!!")
                                ign_heading['align'] = "center"
                                ign_heading['style'] = "color: black;"
                                ign_heading['id'] = "{ign}{suit}".format(ign="ign",
                                                                         suit=suitname.attrib["name"].split(".")[2])
                            else:
                                # print ignition logs present
                                # start add the ignition log in the report
                                ign_heading = h3("All Ignition Report")
                                ign_heading['align'] = "center"
                                ign_heading['style'] = "color: black;"
                                ign_heading['id'] = "{ign}{suit}".format(ign="ign",
                                                                         suit=suitname.attrib["name"].split(".")[2])
                                ign_table = table()
                                ign_table.set_attribute("class",
                                                        "table table-striped table-bordered table-condensed table-hover")
                                # create the table for the ignition logs
                                with ign_table.add(tbody()):
                                    th("IGN Name")
                                    th("Test Case\n(in which ignition happend)")
                                    th("Suit Name")
                                    th("Module Name")
                                    th("Time(Target Time)")
                                    th("Logs")
                                    for ignition in suitname.iter("ignition"):
                                        tr_ign = tr()
                                        tr_ign += td(ignition.attrib["name"])
                                        with tr_ign:
                                            td(ignition.attrib["testcasename"])
                                            td(ignition.attrib["suitname"])
                                            td(ignition.attrib["modulename"])
                                            td(ignition.attrib["time"])
                                            ign_log_file_path = os.path.join(module_name.attrib["name"], "IgnitionLog",
                                                                             ignition.attrib["logfilename"])
                                            td(a("Log File", href="./%s" % ign_log_file_path, target="_blank",
                                                 rel="noopener noreferrer"))
                            # add the test table and ignition table in module div
                            module_name_div.add(ign_heading)
                            if ign_table is not None:
                                module_name_div.add(ign_table)
                            # add crash log data
                            crash_div = div()
                            crash_div.set_attribute("id", "#{crash}{suit}".format(crash="crash",
                                                                                  suit=
                                                                                  suitname.attrib["name"].split(".")[
                                                                                      2]))
                            with crash_div:
                                crash_log_heading = h3("Crash Logs")
                                crash_log_heading['align'] = "center"
                                crash_log_heading['style'] = "color: black;"
                                test_report_heading['id'] = "#{crash}{suit}".format(crash="crash",
                                                                                    suit=
                                                                                    suitname.attrib["name"].split(".")[
                                                                                        2])
                                crash_log_table = table()
                                crash_log_table.set_attribute('class',
                                                              'table table-striped table-bordered table-condensed table-hover')
                                with crash_log_table.add(tbody()):
                                    th("Name")
                                    th("Test Case Name")
                                    th("Suit Name")
                                    th("Module Name")
                                    th("Packages")
                                    th("Logs")
                                    for crash_data in suitname.iter("crashinfo"):
                                        l = tr()
                                        l += td(crash_data.attrib["name"])
                                        with l:
                                            td(crash_data.attrib["testcasename"])
                                            td(crash_data.attrib["suitname"])
                                            td(crash_data.attrib["modulename"])
                                            td(crash_data.attrib["packagelist"])
                                            log_file_path = os.path.join("CrashLogsReport", "Crash_logs.log")
                                            crash_log_file_path = os.path.join(self.get_crash_log_path,
                                                                               "Crash_logs.log")
                                            logger.console("xml crash logs path is : %s" % log_file_path)
                                            td(a("Log File", href="./%s" % log_file_path, target="_blank",
                                                 rel="noopener noreferrer"))
                            # add row in the summary div to add "SUIT" info of PASS And FAIL cases
                            tr_suit_summary.add(td(s_test_pass + s_test_fail))
                            tr_suit_summary.add(td(s_test_pass))
                            tr_suit_summary.add(td(s_test_fail))
                            test_summary_table.add(tr_suit_summary)
                        # add the row in the summary div to add "MODULE" info of PASS And FAIL cases
                        tr_module_summary.add(td(m_test_pass + m_test_fail))
                        tr_module_summary.add(td(m_test_pass))
                        tr_module_summary.add(td(m_test_fail))
                        test_summary_table.add(tr_module_summary)
                div_test_summary.add(test_summary_table)
            with summary_info_div:
                # TODO: all the value here
                if total_test_fail > 0:
                    status_span = span("STATUS: %s cases are failed" % total_test_fail)
                    status_span.set_attribute("class", "col-md-12")
                    status_span.set_attribute("style", "color: red")
                else:
                    status_span = span("STATUS: All test cases pass")
                    status_span.set_attribute("class", "col-md-12")
                    status_span.set_attribute("style", "color: green")
                total_span = span("TOTAL TEST CASES: %s" % str(total_test_fail + total_test_pass))
                total_span.set_attribute("class", "col-md-12")
                total_pass_span = span("TOTAL PASS TEST CASES: %s" % str(total_test_pass))
                total_pass_span.set_attribute("class", "col-md-12")
                total_fail_span = span("TOTAL FAIL TEST CASES: %s" % str(total_test_fail))
                total_fail_span.set_attribute("class", "col-md-12")
                for exec_info in CreateXmlReport.ROOT.iter("execinfo"):
                    start_time_span = span("START TIME: %s" % exec_info.attrib['starttime'])
                    start_time_span.set_attribute("class", "col-md-12")
                    end_time_span = span("END TIME: %s" % exec_info.attrib['endtime'])
                    end_time_span.set_attribute("class", "col-md-12")
                    build_number_span = span("BUILD INFO: %s" % exec_info.attrib['buildinfo'])
                    build_number_span.set_attribute("class", "col-md-12")

            print("HTML Path: %s" % self.get_report_path)
            logger.console("HTML Path: %s" % self.get_report_path)
            save_file_path = os.path.join(self.get_report_path, "CustomReport.html")
            with open(save_file_path, "w") as fp:
                fp.write(str(doc))
                fp.close()
            logger.console("Report creation finish...!!")
        except Exception as exp:
            print("XML to HTML parsing error, EXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            logger.console(exc_type, fname, exc_tb.tb_lineno)
