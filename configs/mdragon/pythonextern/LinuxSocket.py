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
        if rev!='\n':
            data += rev
        else:
            print("SERVER",data)
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
    
    def __init__(self,linuxc):
        #self.lcnc_star = lcnc_star
        #self.lcnc_cmd = lcnc_cmd
        self.state = 0
        threading.Thread.__init__(self)
        self.linuxcncs = linuxc
        self.lcnc_star = self.linuxcncs.stat() # create a connection to the status channel
        self.lcnc_cmd = self.linuxcncs.command()

        
    def run(self):
        global server_get
        timebegin = 0
        while (1):
           
            if (server_get["status"]  == True):
                print("havevari ",server_get["data"] )
                server_get["status"] = False
                try:
                    data = json.loads(server_get["data"])
                except Exception as e:
                    print(e)
                    continue
                if "MDI" in data["sts"]:
                    self.call_MDI(data["data"])
                elif "RST" in data["sts"]:
                    self.state = 0
                elif "SET" in data["sts"]:
                    self.call_Set(data["data"],data["arg"])
                elif "tMDI" in data["sts"]:
                    self.call_tMDI(data["data"])
            
            if (self.state == 1):
                if self.lcnc_cmd.wait_complete(0.001) != -1:
                    self.state = 2
            elif (self.state == 2):
                self.sendBack_server("Done\n")
                self.state = 0
            if (time.time()-timebegin > 1):
                timebegin =  time.time()
                
    def call_MDI(self, cmd):
        if self.state == 0:  
            self.lcnc_cmd.mdi(cmd)
            self.state = 1
        else:
            print("Wait")   
            self.sendBack_server("Wait\n")
    #{"sts":"SET","data":"mode","arg":["MODE_MDI",1,2.1]}
    #{"sts":"SET","data":"mode","arg":"MODE_MDI"}   ->c.mode(linuxcnc.MODE_MDI)
    #{"sts":"SET","data":"mode","arg":"MODE_AUTO"}  ->c.mode(linuxcnc.MODE_AUTO)
    #{"sts":"SET","data":"mode","arg":"MODE_MANUAL"}->c.mode(linuxcnc.MODE_MANUAL)
    def call_Set(self, cmd,arg):
        size = len(arg)
        print(" ARG have size : ",size)
        listpara = [None] * size
        for s in arg:
            print("The type is : ",s,"is", type(s).__name__)
            #type(i) is int  ->True
        for x in range(size):
            print("The type rais : ",arg[x],"is", type(arg[x]).__name__)
            if type(arg[x]) is str:
                listpara[x]=getattr(self.linuxcncs,arg[x])
            else:
                listpara[x]=arg[x]

        if self.state == 0:
            if (size == 0):
                getattr(self.lcnc_cmd, cmd)
            else:
                getattr(self.lcnc_cmd, cmd)(*listpara)
            self.state = 1
        else:
            print("Wait")   
            self.sendBack_server("Wait\n")       

    def fun(self,samp_list):
        return ",".join(samp_list)         
    def get_listpara(self,arg):
        pass    

    def call_tMDI(self, cmd):
        print("Call MDI",cmd)

    def sendBack_server(self,cmd):
        global handler
        if handler == None:
            return
        handler.sendData(cmd)

if __name__ == '__main__':

    ar = AsyncoreRunner()
    ar.daemon = True
    ar.start()
    li = Linuxcnc_cmd(linuxcnc)
    li.daemon = True
    li.start()
    def exit_handler():
        print('My application is ending!')
    atexit.register(exit_handler)
    while(1):
        time.sleep(1)
