from time import time
from time import sleep
import threading
import sys, traceback

class mytimer(threading.Thread):
    """My timer class
    calls callback once every period (in seconds).  callback takes no
    arguements.  
    Also, note that call backs are /periodic/ with the EXACT 
    average period of period. Unlike the threading.Timer class, clock jitter
    does NOT accumulate! 
    
    Not sure what the smallest period possible is. 3 seconds is def good.
    """
    
    def __init__(self,period,callback):
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
        return int(base * round(float(x)/base))

    def _mytime(self):
        return time()-self.starttime
        
    def run(self):
        while self.go:
            next_time = self._myround(self._mytime()+self.p,self.p)
            try:
                self.cb()
            except:
                traceback.print_exc(file=sys.stdout)
                f = open('errors.log',"a")
                t = time()
                f.write('===== time:' +str(t)+ '\n' )
                traceback.print_exc(file=f)
                f.close()
                
            #sleep until next_time
            while self._mytime() < (next_time-0.01) and self.go:
                dt = next_time-self._mytime()
                if dt>1:
                    dt = 1
                sleep(dt)
    

def _callme():
        print "tick: " + str(time())
    
if __name__ == '__main__':
    mt = mytimer(3,_callme)
    mt.start()
