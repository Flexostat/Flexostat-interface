from controller import Controller as ServoStatController
from ConfigParser import SafeConfigParser

import threading
import unittest

class MockSerialPort():
	"""Mock serial port object with a .lock attribute.
	
	Has a lock attribute because servostat.py attaches a reader
	lock to the ports before passing them to the controller.
	"""
	
	def __init__(self, *args, **kwargs):
		self.lock = threading.RLock()
		self.write_log = []
		self.in_buffer = []  # FIFO buffer of lines.
	
	def write(self, val):
		self.write_log.append(val)
		
	def inWaiting(self):
		return sum(map(len, self.in_buffer))
	
	def readline(self):
		return self.in_buffer.pop(0)
		
	def _appendToInBuffer(self, msg):
		self.in_buffer.append(msg)



class ServoStatControllerTest(unittest.TestCase):
	"""Trivial testing of the Controller. 
	
	To ensure simple changes haven't broken it.
	"""
	
	def setUp(self):
		"""Called once before each test is run."""
	    # Read test configuration from the test config file
		config = SafeConfigParser()
		config.read('test/test_config.ini')
		
		self.controller_params = dict(config.items('controller'))
		self.pump_params = dict(config.items('pump'))
		self.logs = dict(config.items('log'))
		self.mock_control_port = MockSerialPort()
		self.mock_pump_port = MockSerialPort()
		self.controller = ServoStatController(self.controller_params,
								   			  self.logs,
										 	  self.pump_params,
											  self.mock_control_port,
											  self.mock_pump_port)
	
	def tearDown(self):
		self.controller.quit()
		
	def testSerialCheckNoOutput(self):
		self.controller.serialCheck()
	
	def testSerialCheckWithOutput(self):
		output_ods = ['10', '200'] * 8
		output_ods = ' '.join(output_ods)
		self.mock_control_port._appendToInBuffer(output_ods)
		self.controller.serialCheck()
	

if __name__ == '__main__':
	unittest.main()