import socket
import atexit
import os,sys, threading, logging
import asyncore
import time
import queue
import json
import linuxcnc
queue  = queue.Queue(10)
#sudo netstat -ap | grep :8080

"""

sudo lsof -t -i tcp:8080 | xargs kill -9
"""
server_get = {"status":False,"data":""}
handler = None
data=""
class EchoHandler(asyncore.dispatcher_with_send):
    
    def handle_read(self):
        global server_get
        global data
        rev = self.recv(1)
        rev = rev.decode("utf8")
        print("SERVER",rev)
        if rev!='\n':
            data += rev
        else:
            str_data = data #.decode("utf8")
            data = ''

            server_get["status"] = True
            server_get["data"]=str_data

    def sendData(self,data):
        self.send(data.encode())

    def handle_close(self):
        self.close()
        print("CLOSE")

"""class EchoServer(asyncore.dispatcher):
    
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        #socket.TCPServer.allow_reuse_address = True
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        global handler
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock)"""


class AsyncoreRunner(threading.Thread,asyncore.dispatcher):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.server = EchoServer('0.0.0.0', 8080)
        asyncore.dispatcher.__init__(self)
        #socket.TCPServer.allow_reuse_address = True
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('0.0.0.0', 8080))
        self.listen(5)
    def ping(self):
        pass

    def run(self):
        print (' thread start')
        asyncore.loop()
        print (' thread stop')

    def handle_accept(self):
        global handler
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock)

    def close(self):
        self.server.close()
        self.join()


class Linuxcnc_cmd(threading.Thread):
    
    def __init__(self,lcnc_star,lcnc_cmd):
        self.lcnc_star = lcnc_star
        self.lcnc_cmd = lcnc_cmd
        self.state = 0
        threading.Thread.__init__(self)


        
    def run(self):
        global server_get
        timebegin = 0
        while (1):
            if (server_get["status"]  == True):
                print("havevari ",server_get["data"] )
                data = json.loads(server_get["data"])
                server_get["status"] = False
                if "MDI" in data["sts"]:
                    self.call_MDI(data["data"])
                elif "RST" in data["sts"]:
                    self.state = 0
                elif "tMDI" in data["sts"]:
                    self.call_tMDI(data["data"])
            
            if (self.state == 1):
                print("TIME B",time.time())
                if self.lcnc_cmd.wait_complete(0.1) != -1:
                    self.state = 2
                print("TIME E",time.time())
            elif (self.state == 2):
                self.sendBack_server("Done\n")
                self.state = 0
            if (time.time()-timebegin > 1):
                timebegin =  time.time()
                print("self.lcnc_cmd.wait_complete()",self.lcnc_cmd.wait_complete())    

    def call_MDI(self, cmd):
        if self.state == 0:  
            print("Call MDI",cmd)
            self.lcnc_cmd.mdi(cmd)
            print("End Call MDI",cmd)
            self.state = 1
        else:
            print("Wait")   
            self.sendBack_server("Wait\n")

    def call_tMDI(self, cmd):
        print("Call MDI",cmd)

    def sendBack_server(self,cmd):
        global handler
        if handler == None:
            return
        handler.sendData(cmd)

if __name__ == '__main__':
    s = linuxcnc.stat() # create a connection to the status channel
    #s.poll() # get current values
    c = linuxcnc.command()
    ar = AsyncoreRunner()
    ar.daemon = True
    ar.start()
    li = Linuxcnc_cmd(s,c)
    li.daemon = True
    li.start()
    def exit_handler():
        print('My application is ending!')
    atexit.register(exit_handler)
    while(1):
        time.sleep(1)
