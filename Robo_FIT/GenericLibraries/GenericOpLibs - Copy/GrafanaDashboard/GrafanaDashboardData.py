from Robo_FIT.GenericLibraries.GenericOpLibs.GrafanaDashboard.BootKpiData import BootKpiData
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *


class GrafanaDashboardData:

    def __init__(self):
        self.boot_kpi = BootKpiData()

    def upload_data(self):
        """
        Post data and json_data to API endpoint given specific URL.
        :param: column_names_list provide the required column values as in form of list.
        """
        self.boot_kpi.upload_bootkpi_data()
