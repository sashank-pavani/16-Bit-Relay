
import struct
import serial
import time
import threading
import logging

CMD_RELAY_CTL  = 0x00;
CMD_CAN_RX_MON = 0x01;
CMD_CAN_TX     = 0x02;
CMD_CAN_INIT   = 0x03;
CMD_CAN_RX     = 0x04;
CMD_I2C_INIT   = 0x05;
CMD_I2C_W      = 0x06;
CMD_I2C_R      = 0x07;
CMD_I2C_WR     = 0x08;
CMD_ANA_REF    = 0x09;
CMD_ANA_READ   = 0x0A;
CMD_DIO_DIR    = 0x0B;
CMD_DIO_SET    = 0x0C;
CMD_DIO_GET    = 0x0D;
CMD_LAST       = 0x0E;

STS_UNKNOWN    = 0
STS_OK         = 1
STS_FAIL       = 2

ANA_REF_5V     = 0x00;
ANA_REF_EXT    = 0xFF;

DIO_DIR_IN     = 0x00;
DIO_DIR_OUT    = 0x01;

DIO_VAL_LOW    = 0x00;
DIO_VAL_HIGH   = 0x01;

i2c_read_data = bytearray()
response = bytearray(CMD_LAST)
can_rx_callback = None

resp_event = threading.Event()
ser_con = serial.Serial();
relay_mask = 0x00
ana_value = 0
dio_value = 0
last_message = ""

def rx_thread_ser_con():
	global response
	global i2c_read_data
	global ana_value
	global dio_value
	print("Rx Thread Started")	
	while(1):
		try:
			num_bytes = int.from_bytes(ser_con.read(size=1), byteorder='big')
			data = ser_con.read(num_bytes - 1)

			if(len(data) > 1 and data[0] == CMD_RELAY_CTL):
				if(data[1] == relay_mask):
					response[CMD_RELAY_CTL] = STS_OK
				else:
					response[CMD_RELAY_CTL] = STS_FAIL
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_I2C_INIT):
				if(data[2] == 0x01):
					response[CMD_I2C_INIT] = STS_OK
				else:
					response[CMD_I2C_INIT] = STS_FAIL
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_I2C_W):
				if(data[len(data) - 1] == 0x00):
					response[CMD_I2C_W] = STS_OK
				else:
					response[CMD_I2C_W] = STS_FAIL
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_I2C_R):
				i2c_read_data = bytearray()
				for i in range(3, len(data)):
					i2c_read_data.append(data[i])
				response[CMD_I2C_R] = STS_OK
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_I2C_WR):
				tx_len = data[2]
				rx_len = data[tx_len + 4]
				rx_idx = data[2] + 5
				i2c_read_data = bytearray()
				for i in range(rx_idx, rx_idx + rx_len):
					i2c_read_data.append(data[i])
				response[CMD_I2C_WR] = STS_OK
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_CAN_INIT):
				if(data[2] == 0x01):
					response[CMD_CAN_INIT] = STS_OK
				else:
					response[CMD_CAN_INIT] = STS_FAIL
				resp_event.set()
			elif(len(data) > 2 and data[0] == CMD_CAN_RX_MON):
				if(data[2] == 0x01):
					response[CMD_CAN_RX_MON] = STS_OK
				else:
					response[CMD_CAN_RX_MON] = STS_FAIL
				resp_event.set()
			elif(len(data) > 11 and data[0] == CMD_CAN_TX):
				if(data[11] == 0x01):
					response[CMD_CAN_TX] = STS_OK
				else:
					response[CMD_CAN_TX] = STS_FAIL
				resp_event.set()
			elif(len(data) > 11 and data[0] == CMD_CAN_RX):
				if can_rx_callback is not None:
					id = data[1] << 8 | data[2]
					logging.info("CMD_CAN_RX : " + format(id, '#06x') + " " + format(data[3], '#04x') + " " + format(data[4], '#04x') + " " + format(data[5], '#04x') + " " + format(data[6], '#04x') + " " + format(data[7], '#04x') + " " + format(data[8], '#04x') + " " + format(data[9], '#04x') + " " + format(data[10], '#04x'))
					can_rx_callback(data)
			elif(len(data) == 2 and data[0] == CMD_ANA_REF):
				response[CMD_ANA_REF] = STS_OK
				resp_event.set()
			elif(len(data) == 4 and data[0] == CMD_ANA_READ):
				ana_value = ((data[2] << 8) | data[3])
				response[CMD_ANA_READ] = STS_OK
				resp_event.set()
			elif(len(data) == 3 and data[0] == CMD_DIO_DIR):
				response[CMD_DIO_DIR] = STS_OK
				resp_event.set()
			elif(len(data) == 3 and data[0] == CMD_DIO_SET):
				response[CMD_DIO_SET] = STS_OK
				resp_event.set()
			elif(len(data) == 3 and data[0] == CMD_DIO_GET):
				response[CMD_DIO_GET] = STS_OK
				dio_value = data[2]
				resp_event.set()
			else:
				response[CMD_RELAY_CTL] = STS_FAIL
				response[CMD_CAN_INIT] = STS_FAIL
				response[CMD_CAN_RX_MON] = STS_FAIL
				response[CMD_CAN_TX] = STS_FAIL
				response[CMD_I2C_INIT] = STS_FAIL
				response[CMD_I2C_R] = STS_FAIL
				response[CMD_I2C_W] = STS_FAIL
				response[CMD_I2C_WR] = STS_FAIL
				response[CMD_ANA_REF] = STS_FAIL
				response[CMD_ANA_READ] = STS_FAIL
				response[CMD_DIO_DIR] = STS_FAIL
				response[CMD_DIO_SET] = STS_FAIL
				response[CMD_DIO_GET] = STS_FAIL
				resp_event.set()
		except serial.SerialException:
			print ("Exception")


def init( port ):
	print("Connecting to " + port)
	
	logging.basicConfig(filename='vAutoKit.log', level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	logging.Formatter(fmt='%(asctime)s.%(msecs)03d',datefmt='%Y-%m-%d,%H:%M:%S')
	
	try:
		ser_con.port=port
		ser_con.baudrate=100000
		ser_con.bytesize=8
		ser_con.stopbits=serial.STOPBITS_ONE
		ser_con.open()
		time.sleep(2)
		rx_thread = threading.Thread(target=rx_thread_ser_con)
		rx_thread.daemon = True
		rx_thread.start()
	except serial.SerialException:
		print ("USB Console open error " + port + ". Please close other open tabs / ports.")

def set_relay(idx, on):
	global response
	global relay_mask
	
	response[CMD_RELAY_CTL] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_RELAY_CTL)
	if(on):
		relay_mask |= (0x01 << idx)
	else:
		relay_mask &= ~(0x01 << idx)
	cmd.append(relay_mask)
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_RELAY_CTL] = STS_FAIL
	
	if(response[CMD_RELAY_CTL] == STS_OK):
		logging.info("CMD_RELAY_CTL : " + hex(relay_mask))
	
	return response[CMD_RELAY_CTL]

def can_init(speed):
	global response
	
	response[CMD_CAN_INIT] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_CAN_INIT)
	
	if(speed == 512000):
		cmd.append(0x01)
	else:
		cmd.append(0x00)

	resp_event.clear()	
	ser_con.write(cmd)

	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_CAN_INIT] = STS_FAIL

	if(response[CMD_CAN_INIT] == STS_OK):
		logging.info("CMD_CAN_INIT : " + str(speed) + " - Pass")
	else:
		logging.info("CMD_CAN_INIT : " + str(speed) + " - Fail")

	return response[CMD_CAN_INIT]

def can_rx_mon_enable(enable, callback = None):
	global response
	global can_rx_callback
	
	if callback:
		can_rx_callback = callback
	
	response[CMD_CAN_RX_MON]  = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_CAN_RX_MON)
	
	if(enable == 1):
		cmd.append(0x01)
	else:
		cmd.append(0x00)

	resp_event.clear()	
	ser_con.write(cmd)

	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_CAN_RX_MON]  = STS_FAIL

	if(response[CMD_CAN_RX_MON]  == STS_OK):
		logging.info("CMD_CAN_RX_MON : " + str(enable) + " - Pass")
	else:
		logging.info("CMD_CAN_RX_MON : " + str(enable) + " - Fail")

	return response[CMD_CAN_RX_MON] 


def can_tx(id, data):
	global response
	response[CMD_CAN_TX]  = STS_UNKNOWN
	
	cmd = bytearray()
	cmd.append(CMD_CAN_TX)

	id_arr = id.to_bytes( 2, "big" )
	cmd.append(id_arr[0])
	cmd.append(id_arr[1])
	cmd.append(data[0])
	cmd.append(data[1])
	cmd.append(data[2])
	cmd.append(data[3])
	cmd.append(data[4])
	cmd.append(data[5])
	cmd.append(data[6])
	cmd.append(data[7])
	
	resp_event.clear()
	ser_con.write(cmd)

	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_CAN_TX]  = STS_FAIL
	
	if(response[CMD_CAN_TX]  == STS_OK):
		logging.info("CMD_CAN_TX : " + format(id, '#06x') + " " + format(data[0], '#04x') + " " + format(data[1], '#04x') + " " + format(data[2], '#04x') + " " + format(data[3], '#04x') + " " + format(data[4], '#04x') + " " + format(data[5], '#04x') + " " + format(data[6], '#04x') + " " + format(data[7], '#04x'))
	else:
		logging.info("CMD_CAN_TX : " + format(id, '#06x') + " " + format(data[0], '#04x') + " " + format(data[1], '#04x') + " " + format(data[2], '#04x') + " " + format(data[3], '#04x') + " " + format(data[4], '#04x') + " " + format(data[5], '#04x') + " " + format(data[6], '#04x') + " " + format(data[7], '#04x') + " - FAIL")
	
	return response[CMD_CAN_TX] 

def i2c_master_init(speed):
	global response
	
	response[CMD_I2C_INIT] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_I2C_INIT)
	#Master Mode
	cmd.append(0x01)
	
	if(speed == 400000):
		cmd.append(0x01)
	elif(speed == 1000000):
		cmd.append(0x02)
	elif(speed == 3400000):
		cmd.append(0x03)
	else:
		cmd.append(0x00)

	resp_event.clear()	
	ser_con.write(cmd)

	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_I2C_INIT] = STS_FAIL

	if(response[CMD_I2C_INIT] == STS_OK):
		logging.info("CMD_I2C_INIT : " + str(speed) + " - Pass");
	else:
		logging.info("CMD_I2C_INIT : " + str(speed) + " - Fail");

	return response[CMD_I2C_INIT]

def i2c_master_write(addr, data):
	global response
	response[CMD_I2C_W]  = STS_UNKNOWN
	
	cmd = bytearray()
	cmd.append(CMD_I2C_W)
	cmd.append(addr)
	cmd.append(len(data))

	for i in range(len(data)):
		cmd.append(data[i])
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_I2C_W]  = STS_FAIL
	
	log_msg = "CMD_I2C_W : " + format(addr, '#04x')
	for i in range(len(data)):
		log_msg += " " + format(data[i], '#04x')
	
	if(response[CMD_I2C_W]  == STS_OK):
		logging.info(log_msg + " - PASS")
	else:
		logging.info(log_msg + " - FAIL")
	
	return response[CMD_I2C_W] 

def i2c_master_read(addr, data):
	global response
	global i2c_read_data
	response[CMD_I2C_R]  = STS_UNKNOWN
	
	cmd = bytearray()
	cmd.append(CMD_I2C_R)
	cmd.append(addr)
	cmd.append(len(data))
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_I2C_R]  = STS_FAIL
	
	if len(i2c_read_data) == len(data):
		response[CMD_I2C_R]  = 1
	else:
		response[CMD_I2C_R]  = STS_FAIL
	
	log_msg = "CMD_I2C_R : " + format(addr, '#04x')
	
	for i in range(len(data)):
		data[i] = i2c_read_data[i]
		log_msg += " " + format(data[i], '#04x')
	
	if(response[CMD_I2C_R]  == STS_OK):
		logging.info(log_msg + " - PASS")
	else:
		logging.info(log_msg + " - FAIL")
	
	return response[CMD_I2C_R] 

def i2c_master_write_read(addr, tx_data, rx_data):
	global response
	response[CMD_I2C_WR]  = STS_UNKNOWN
	
	cmd = bytearray()
	cmd.append(CMD_I2C_WR)
	cmd.append(addr)
	cmd.append(len(tx_data))

	for i in range(len(tx_data)):
		cmd.append(tx_data[i])
	
	cmd.append(len(rx_data))
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_I2C_WR]  = STS_FAIL
	
	if len(i2c_read_data) == len(rx_data):
		response[CMD_I2C_WR]  = STS_OK
	else:
		response[CMD_I2C_WR]  = STS_FAIL
		
	log_msg = "CMD_I2C_WR : " + format(addr, '#04x')
	
	for i in range(len(tx_data)):
		log_msg += " " + format(tx_data[i], '#04x')

	for i in range(len(rx_data)):
		rx_data[i] = i2c_read_data[i]
		log_msg += " " + format(rx_data[i], '#04x')
		
	if(response[CMD_I2C_WR]  == STS_OK):
		logging.info(log_msg + " - PASS")
	else:
		logging.info(log_msg + " - FAIL")
	
	return response[CMD_I2C_WR] 

def set_ana_ref(ref):
	global response
	
	response[CMD_ANA_REF] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_ANA_REF)
	cmd.append(ref)
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_ANA_REF] = STS_FAIL
	
	if(response[CMD_ANA_REF] == STS_OK):
		logging.info("CMD_ANA_REF : " + hex(ref))
	
	return response[CMD_ANA_REF]

def ana_read(pin):
	global response
	global ana_value
	
	ana_value = 0
	response[CMD_ANA_READ] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_ANA_READ)
	cmd.append(pin)
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_ANA_READ] = STS_FAIL
	
	if(response[CMD_ANA_READ] == 1):
		logging.info("CMD_ANA_READ : " + hex(pin) + " " + hex(ana_value))
	
	return response[CMD_ANA_READ], ana_value

def set_dio_dir(pin, dir):
	global response
	
	response[CMD_DIO_DIR] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_DIO_DIR)
	cmd.append(pin)
	cmd.append(dir)
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_DIO_DIR] = STS_FAIL
	
	if(response[CMD_DIO_DIR] == STS_OK):
		logging.info("CMD_DIO_DIR : " + hex(pin) + " " + hex(dir))
	
	return response[CMD_DIO_DIR]

def set_dio_val(pin, val):
	global response
	
	response[CMD_DIO_SET] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_DIO_SET)
	cmd.append(pin)
	cmd.append(val)
	
	resp_event.clear()
	ser_con.write(cmd)
	
	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_DIO_SET] = STS_FAIL
	
	if(response[CMD_DIO_SET] == STS_OK):
		logging.info("CMD_DIO_SET : " + hex(pin) + " " + hex(val))
	
	return response[CMD_DIO_SET]

def get_dio_val(pin):
	global response
	global dio_value
	
	dio_value = 0
	response[CMD_DIO_GET] = STS_UNKNOWN
	cmd = bytearray()
	cmd.append(CMD_DIO_GET)
	cmd.append(pin)
	
	resp_event.clear()
	ser_con.write(cmd)

	event_set = resp_event.wait(1)
	if not event_set:
		response[CMD_DIO_GET] = STS_FAIL

	if(response[CMD_DIO_GET] == STS_OK):
		logging.info("CMD_DIO_GET : " + hex(pin) + " " + hex(dio_value))
	
	return response[CMD_DIO_GET], dio_value
