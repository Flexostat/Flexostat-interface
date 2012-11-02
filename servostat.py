from controller import Controller
from ConfigParser import SafeConfigParser
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
    #convert all keys to floats
    #in retrospect, this was a mistake... but old sections of code rely on this
    #and I don't want to refactor that code right now.
    for key in controller_params:
        if key == "controlfun":
            pass            
        else:
            controller_params[key] = float(controller_params[key])
    
    port_names = dict(config.items('ports'))
    pump_params = dict(config.items('pump'))
    logs = dict(config.items('log'))

    #open ports
    cont_port = serial.Serial(port_names['controllerport'],
                              int(controller_params['baudrate']),timeout = 4)
    cont_port.lock = threading.RLock()
    if (port_names['pumpport'].upper()!='NONE'):
        pump_port = serial.Serial(port_names['pumpport'],
                                  int(pump_params['baudrate']),timeout = 1)
        pump_port.lock = threading.RLock()
    else:
        pump_port = None
    
    #make the controler
    cont = Controller(controller_params,logs,pump_params,
                                 cont_port, pump_port)
    
    
    print 'num threads: ' + str(len(sys._current_frames().keys()))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print 'shutting down'
        cont.quit()
        time.sleep(1.1)
        
