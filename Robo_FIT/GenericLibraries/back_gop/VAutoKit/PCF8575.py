#from vAutoKit import vAutoKit
import time
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.Vautokit import VautokitAPI
slave_Address = 0x20
bank0_dir = 0xFF
bank1_dir = 0xFF
bank0_out = 0xFF
bank1_out = 0xFF

STS_UNKNOWN    = 0
STS_OK         = 1
STS_FAIL       = 2

DIO_DIR_IN     = 0x00
DIO_DIR_OUT    = 0x01

DIO_VAL_LOW    = 0x00
DIO_VAL_HIGH   = 0x01

def PCF8575_init( address ):
	global slave_address
	
	slave_Address = address
	status = VautokitAPI.i2c_master_init(1000000)
	
	return status

def set_dio_dir(pin, dir):
	global slave_Address 
	global bank0_dir
	global bank1_dir

	if pin < 8:
		bank0_dir |= (1 << pin)
		status = STS_OK
	elif pin < 16:
		bank1_dir |= (1 << (pin - 8))
		status = STS_OK
	else:
		status = STS_FAIL
	
	return status

def set_dio_val_50ms(pin, val):
	global slave_Address 
	global bank0_dir
	global bank1_dir
	global bank0_out
	global bank1_out
	if 1:
		data1 = bytearray()
		data1.append(bank0_out)
		data1.append(bank1_out)

	if pin < 8:
		pin_mask = 1 << pin
		if bank0_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank0_out |= pin_mask 
			else:
				bank0_out &= ~pin_mask 
			status = STS_OK
		else:
			status = STS_FAIL
	elif pin < 16:
		pin_mask = (1 << (pin - 8))
		if bank1_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank1_out |= pin_mask 
			else:
				bank1_out &= ~pin_mask 
			status = STS_OK
		else:
			status = STS_FAIL
	else:
		status = STS_FAIL

	data = bytearray()
	data.append(bank0_out)
	data.append(bank1_out)

	# PCF8575_init(0x20)
	status = VautokitAPI.i2c_master_write(slave_Address, data)
	time.sleep(750/1000)
	# PCF8575_init(0x20)
	status = VautokitAPI.i2c_master_write(slave_Address, data1)
	
	return status


def set_dio_val_4s(pin, val):
	global slave_Address
	global bank0_dir
	global bank1_dir
	global bank0_out
	global bank1_out
	if 1:
		data1 = bytearray()
		data1.append(bank0_out)
		data1.append(bank1_out)

	if pin < 8:
		pin_mask = 1 << pin
		if bank0_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank0_out |= pin_mask
			else:
				bank0_out &= ~pin_mask
			status = STS_OK
		else:
			status = STS_FAIL
	elif pin < 16:
		pin_mask = (1 << (pin - 8))
		if bank1_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank1_out |= pin_mask
			else:
				bank1_out &= ~pin_mask
			status = STS_OK
		else:
			status = STS_FAIL
	else:
		status = STS_FAIL

	data = bytearray()
	data.append(bank0_out)
	data.append(bank1_out)
	status = VautokitAPI.i2c_master_write(slave_Address, data)
	time.sleep(4)
	status = VautokitAPI.i2c_master_write(slave_Address, data1)

	return status


def set_dio_val(pin, val):
	global slave_Address
	global bank0_dir
	global bank1_dir
	global bank0_out
	global bank1_out

	if pin < 8:
		pin_mask = 1 << pin
		if bank0_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank0_out |= pin_mask
			else:
				bank0_out &= ~pin_mask
			status = STS_OK
		else:
			status = STS_FAIL
	elif pin < 16:
		pin_mask = (1 << (pin - 8))
		if bank1_dir & pin_mask:
			if val == DIO_VAL_HIGH:
				bank1_out |= pin_mask
			else:
				bank1_out &= ~pin_mask
			status = STS_OK
		else:
			status = STS_FAIL
	else:
		status = STS_FAIL

	data = bytearray()
	data.append(bank0_out)
	data.append(bank1_out)
	status = VautokitAPI.i2c_master_write(slave_Address, data)
	return status


def get_dio_val(pin):
	global slave_Address 

	data = bytearray()
	data.append(0x00)
	data.append(0x00)
	status = VautokitAPI.i2c_master_read(slave_Address, data)

	if pin < 8:
		pin_mask = 1 << pin
		dio_value = pin_mask & data[0]
		status = STS_OK
	elif pin < 16:
		pin_mask = (1 << (pin - 8))
		dio_value = pin_mask & data[1]
		status = STS_OK
	else:
		status = STS_FAIL

	return status, (dio_value > 0)
