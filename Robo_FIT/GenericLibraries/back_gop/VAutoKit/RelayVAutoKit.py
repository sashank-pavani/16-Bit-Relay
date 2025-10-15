from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.vAutoKit import vAutoKit
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit import PCF8575
import os
import time


class RelayVAutoKit:

	def __init__(self):
		self.config_manager = ConfigurationManager()

	def turnONPower(self):
		idx = self.config_manager.get_serial_one_power()
		print(idx)
		status = vAutoKit.set_relay(int(idx), 1)
		print(status)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")
	def turnONIgn(self):

		idx = self.config_manager.get_serial_one_ign()
		status = vAutoKit.set_relay(int(idx), 1)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")

	def turnONFlash(self):

		idx = self.config_manager.get_serial_one_flash()
		status = vAutoKit.set_relay(int(idx), 1)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")

	def turnOFFPower(self):

		idx = self.config_manager.get_serial_one_power()
		print(idx)
		status = vAutoKit.set_relay(int(idx), 0)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")

	def turnOFFIgn(self):

		idx = self.config_manager.get_serial_one_ign()
		status = vAutoKit.set_relay(int(idx), 0)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")

	def turnOFFFlash(self):

		idx = self.config_manager.get_serial_one_flash()
		status = vAutoKit.set_relay(int(idx), 0)
		if(status == 1):
			print("Pass")
		else:
			print("Fail")

	def Sendcan(self):

		data = bytearray()
		data.append(0x38)
		data.append(0x00)
		data.append(0x00)
		data.append(0x00)
		data.append(0x00)
		data.append(0x00)
		data.append(0x00)
		data.append(0x00)
		print(data)
		status = vAutoKit.can_tx(0x3B7, data)
		if (status == 1):

			print("Pass")
		else:
			print("Fail")


	def autokit_init(self):
		COM = self.config_manager.get_serial_one_port()

		vAutoKit.init(COM)
		status = PCF8575.init(0x20)
		#status = vAutoKit.can_init(512000)
		if (status == 1):

			print("Pass")
		else:
			print("Fail")

	def pin16bit_realy(self):
		vAutoKit.set_dio_dir(0, vAutoKit.DIO_DIR_IN)


		status = vAutoKit.set_dio_val(0, vAutoKit.DIO_VAL_HIGH)
		if (status == 1):

			print("Pass")
		else:
			print("Fail")
		#time.sleep   2s
		status = vAutoKit.set_dio_val(0, vAutoKit.DIO_VAL_LOW)
		if (status == 1):

			print("Pass")
		else:
			print("Fail")



# if __name__=="__main__":
# 	os.environ["ROBOT_ROOT_PATH"] = r"C:\Swathi\Robo_FW"
# 	os.environ["ROBOT_REPORT_PATH"] = r"C:\Swathi\Robo_FW\CRE\SWE5_SWIntegrationTest\Test_Reports"
# 	os.environ["TEAM_NAME"] = "SWE5_SWIntegrationTest"
# 	a = RelayVAutoKit()
# 	a.autokit_init()
