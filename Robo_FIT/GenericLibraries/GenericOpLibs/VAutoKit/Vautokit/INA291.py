from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.Vautokit import VautokitAPI
#from vAutoKit import vAutoKit

slave_Address_INA291 = 0x40
currentDivider_mA = 10
powerMultiplier_mW = 2

def INA291_init( address ):
	global slave_Address_INA291
	
	slave_Address_INA291 = address
	status = VautokitAPI.i2c_master_init(400000)

	status1 = set_calibration_32V_2A()
	return status,status1

def set_calibration_32V_2A():
	global slave_Address_INA291
	global currentDivider_mA
	global powerMultiplier_mW

	currentDivider_mA = 10
	powerMultiplier_mW = 2
	
	data = bytearray()
	data.append(0x05)
	data.append(0x10)
	data.append(0x00)
	status = VautokitAPI.i2c_master_write(slave_Address_INA291, data)
	
	return status

def getShuntVoltage_mV():
	global slave_Address_INA291

	shunt_vol_raw = 0
	tx_data = bytearray(1)
	rx_data = bytearray(2)

	tx_data[0] = 0x01
	status = VautokitAPI.i2c_master_write_read(0x40, tx_data, rx_data)
	
	if status == 1:
		shunt_vol_raw = rx_data[0] << 8 | rx_data[1];
	
	return ( shunt_vol_raw * 0.01 )

def getBusVoltage_mV():
	global slave_Address_INA291

	bus_vol_raw = 0
	tx_data = bytearray(1)
	rx_data = bytearray(2)

	tx_data[0] = 0x02
	status = VautokitAPI.i2c_master_write_read(0x40, tx_data, rx_data)
	
	if status == 1:
		bus_vol_raw = ((rx_data[0] << 8 | rx_data[1]) >> 3) * 4
	
	return ( bus_vol_raw )

def getPower_mW():
	global slave_Address_INA291
	global powerMultiplier_mW

	power_raw = 0
	tx_data = bytearray(1)
	rx_data = bytearray(2)

	tx_data[0] = 0x03
	status = VautokitAPI.i2c_master_write_read(0x40, tx_data, rx_data)
	
	if status == 1:
		power_raw = ((rx_data[0] << 8 | rx_data[1]) >> 3) * 4
	
	return ( power_raw * powerMultiplier_mW )

def getCurrent_mA():
	global slave_address
	global currentDivider_mA

	current_raw = 0
	tx_data = bytearray(1)
	rx_data = bytearray(2)

	tx_data[0] = 0x04

	status = VautokitAPI.i2c_master_write_read(0x40, tx_data, rx_data)

	if status == 1:
		current_raw = rx_data[0] << 8 | rx_data[1]

	if current_raw & 0x8000 :
		current_raw = 2047 - (current_raw & 0x7FF)

	return current_raw / (1000 * currentDivider_mA)


# def getCurrent_mA():
# 	global slave_address
# 	global currentDivider_mA
#
# 	current_raw = 0
# 	tx_data = bytearray(1)
# 	rx_data = bytearray(2)
#
# 	tx_data[0] = 0x04
#
# 	status = VautokitAPI.i2c_master_write_read(0x40, tx_data, rx_data)
#
# 	# Check the length of rx_data
# 	if len(rx_data) < 2:
# 		raise IndexError("rx_data length is less than expected")
#
# 	# Example i2c_read_data for length check
# 	i2c_read_data = bytearray([0x01, 0x02])
# 	if len(i2c_read_data) < len(rx_data):
# 		raise IndexError("i2c_read_data length is less than rx_data length")
#
# 	if status == 1:
# 		current_raw = rx_data[0] << 8 | rx_data[1]
#
# 	if current_raw & 0x8000:
# 		current_raw = 2047 - (current_raw & 0x7FF)
#
# 	return current_raw / currentDivider_mA

