from controller import Controller as ServoStatController
from ConfigParser import SafeConfigParser

import math
import time
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
    
    def flushInput(self):
    	pass
    	
    def isOpen(self):
    	"""TODO: maybe simulate closed state?"""
    	return True
    
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
        
    def testSerialCheckNoOutput(self):
        self.controller.serialCheck()
    
    def testSerialCheckWithOutput(self):
        tx_val, rx_val = 10, 200
        output_ods = [str(tx_val), str(rx_val)] * 8
        output_ods = ' '.join(output_ods)
        self.mock_control_port._appendToInBuffer(output_ods)
        self.controller.serialCheck()
        
        # Check that the parsing gave the expected values
        expected_tx_vals = [tx_val] * 8
        expected_rx_vals = [rx_val] * 8
        self.assertEquals(expected_rx_vals, self.controller.rx_val)
        self.assertEquals(expected_tx_vals, self.controller.tx_val)
        
    def testStartAndQuit(self):
        # Can't quit before starting.
        self.assertRaises(AssertionError, self.controller.quit)
        self.controller.start()
        
        # Second call to start should fail.
        self.assertRaises(AssertionError, self.controller.start)
        self.controller.quit()  # quit at the end.

    def testStartAndQuitWithDataOnPort(self):
        # Can't quit before starting.
        self.assertRaises(AssertionError, self.controller.quit)
        self.controller.start()
        
        tx_val, rx_val = 10, 200
        output_ods = [str(tx_val), str(rx_val)] * 8
        output_ods = ' '.join(output_ods)
        self.mock_control_port._appendToInBuffer(output_ods)
        time.sleep(10.0)
        
        # Second call to start should fail.
        self.assertRaises(AssertionError, self.controller.start)
        self.controller.quit()  # quit at the end.
    

    def testComputeOD(self):
    	tx, rx = 10, 80
    	btx, brx = 10, 100
    	blank = float(brx) / float(btx)
    	measurement = float(rx) / float(tx)
    	expected_od = math.log10(blank / measurement)
    	actual_od = self.controller.computeOD(btx, brx, tx, rx)
    	self.assertAlmostEquals(expected_od, actual_od, 5)
        

if __name__ == '__main__':
    unittest.main()