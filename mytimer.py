from time import time, sleep

import sys
import traceback
import threading


class mytimer(threading.Thread):
    """Custom timer thread.
    
    Calls a callback once every period (in seconds).
    Callback takes no arguements.  
    
    Also, note that callbacks are /periodic/ with the EXACT 
    average period of period. Unlike the threading.Timer class, clock jitter
    does NOT accumulate! 
    
    Not sure what the smallest period possible is. 3 seconds is definitely good.
    """
    
    def __init__(self, period, callback):
    	"""Initialize the timer.
    	
    	Args:
    		period: how frequently to call the callback (seconds).
    		callback: zero-argument function to call.
    	"""
        threading.Thread.__init__(self)
        self.starttime = 0
        self.p = period
        self.cb = callback
        self.go = True
        
    def start(self):
        self.starttime = time()
        threading.Thread.start(self)
    
    def stop(self):
        self.go = False

    def _myround(self, x, base):
    	"""Custom rounding method.
    	
    	Rounds "x" to a number that is divisible by "base".
    	
    	Args:
    		x: value to round.
    		base: return value should be divisble by base.
    	"""
        return int(base * round(float(x)/base))

    def _mytime(self):
        return time() - self.starttime
        
    def run(self):
        while self.go:
            next_time = self._myround(self._mytime()+self.p,self.p)
            try:
                self.cb()
            except:
                traceback.print_exc(file=sys.stdout)
                f = open('errors.log', 'a')
                t = time()
                f.write('===== time:' + str(t)+  '\n' )
                traceback.print_exc(file=f)
                f.close()
                
            # Sleep until next_time
            while self._mytime() < (next_time - 0.01) and self.go:
                dt = next_time - self._mytime()
                if dt > 1:
                    dt = 1
                sleep(dt)
    

def _callme():
	"""Test callback."""
	print "tick: ", str(time())
    
    
if __name__ == '__main__':
    mt = mytimer(3, _callme)
    mt.start()
