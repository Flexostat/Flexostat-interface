from time import sleep, time

#
#  Works with any pump that can be turned off by /closing/ a switch.
#  For the Watson Marlow 101U/R pin 13 is ground and pin 8 is pulled to +5v
#  Either pull 8 low through open collector output or connect pin 8 to 5v
#  signal (referenced to pin 13).
#
#  Assumes RTS is connected to on/off signal and assorting RTS is ON.


class Pump(object):
    debug = False

    def __init__(self, cparams, logfiles, pparams, unused_cport, pport):
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams # All controller parameters live here
        self.pport = pport
        self.last_stop = 0
        try:
          self.off_delay = self.pparams["offdelay"]
        except KeyError:
          self.off_delay = 1.0

        if pport is not None and pport.isOpen():
            self.pport.setRTS(0)
        else:
            raise Exception("pump port not open!")


    def withdraw(self, volume):
        pass

    def dispense(self, volume): #volume is in 50th of a second
        #blocking call
        self.pport.setRTS(1)
        sleep(1.0/50.0*volume)
        self.pport.setRTS(0)
        self.last_stop = time()

    def waitForPumping(self):
        if (self.last_stop+off_delay)-time() > 0:
            sleep((self.last_stop+off_delay)-time())
