from ConfigParser import SafeConfigParser
from plugins.ne500pumpdriver import Pump

import serial
import threading

"""Run to check whether the pump is connected.

1. Initializes the pump. 
2. Withdraws 1050 units.
3. Dispenses 1000 units.
4. Dispenses 50 units.
"""


def Main():
    # Read test configuration from the test config file
    config = SafeConfigParser()
    config.read('test/test_config.ini')
    
    controller_params = dict(config.items('controller'))
    pump_params = dict(config.items('pump'))
    port_names = dict(config.items('ports'))
    logs = dict(config.items('log'))
    pump_port = serial.Serial(port_names['pumpport'],
                              int(pump_params['baudrate']),
                              timeout=1,
                              writeTimeout=1)
    pump_port.lock = threading.RLock()
    
    # Should initialize the pump.
    pumpdriver = Pump(controller_params, logs, pump_params, None, pump_port)
    
    # A little ditty - withdraw, dispense, dispense.
    pumpdriver.withdraw(1050)
    pumpdriver.waitForPumping()
    pumpdriver.dispense(1000)
    pumpdriver.waitForPumping()
    pumpdriver.dispense(50)
    
    
if __name__ == '__main__':
    Main()