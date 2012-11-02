import socket
import pickle
import threading
from time import sleep


class CTBasicServer(threading.Thread):

    def __init__(self,hp,message_cb, delim = '\n'):
        """ hp <= a tuple of (host,port)
            a host '' means interfaces
            
            message_cb <= a callback function for when data is ready
            (data is ready when delim is encountered)
            should return a string meant to be a response.
        """
        threading.Thread.__init__(self)
        self.delim = delim
        self.host_port = hp
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s = soc
        self.quitting = False
        self.daemon = True
        self.mcb = message_cb

    def run(self):
        self.s.bind(self.host_port)
        self.s.listen(5)
        while not self.quitting:
            conn,addr = self.s.accept()
            #check if we unblocked because we need to quit
            if self.quitting:
                return
            
            data = ''
            while True:
                d = conn.recv(2048)
                data += d
                delind = data.find(self.delim)
                #found a delimiter
                if (delind>=0):
                    #send data to callback 
                    send_str = self.mcb(data[0:delind])
                    if send_str:
                        conn.sendall(send_str)
                    data = data[delind+1:]
                #connection has been closed
                if not d:
                    break
            

    def quit(self):
        self.quitting = True
        #connect to self to unblock accept()
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect(('localhost',port))

def __test_cb(data):
    print data
    return 'your data: ' +data

if __name__ == '__main__':
    host = ''
    port = 8888
    t = CTBasicServer((host,port),__test_cb)
    t.start()
    try:
        while True:
            sleep(0.25)
    except KeyboardInterrupt:
        pass #absorb keyboard interrup and quit
    finally:
        t.quit()
        t.join()

