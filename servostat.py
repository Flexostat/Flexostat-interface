from controller import Controller
from ConfigParser import SafeConfigParser
from network import CTBasicServer
import threading
import serial
import sys
import traceback
import time



if __name__ == '__main__':
    #read parameters
    config = SafeConfigParser()
    config.read('config.ini')
    controller_params = dict(config.items('controller'))
    port_names = dict(config.items('ports'))
    pump_params = dict(config.items('pump'))
    logs = dict(config.items('log'))

    #open ports
    cont_port = serial.Serial(port_names['controllerport'],
                              int(controller_params['baudrate']),timeout = 4,
                              writeTimeout = 1)
    cont_port.lock = threading.RLock()
    if (port_names['pumpport'].upper()!='NONE'):
        pump_port = serial.Serial(port_names['pumpport'],
                                  int(pump_params['baudrate']),timeout = 1,
                                  writeTimeout = 1)
        pump_port.lock = threading.RLock()
    else:
        pump_port = None
    
    #make the controler
    cont = Controller(controller_params,logs,pump_params,
                                 cont_port, pump_port)
    
    #setup up network configue port
    def cb(cmd):
        if 'list' in cmd:
            return str(controller_params)
    netserv = CTBasicServer(('',int(port_names['network'])),cb)
    netserv.start()
    
    print 'num threads: ' + str(len(sys._current_frames().keys()))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print 'shutting down'
        cont.quit()
        time.sleep(1.1)
        
