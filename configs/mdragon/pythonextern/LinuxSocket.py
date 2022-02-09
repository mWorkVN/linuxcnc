import socket
import atexit
import os,sys, threading, logging
import asyncore
import time
#sudo netstat -ap | grep :8080

"""

sudo lsof -t -i tcp:8080 | xargs kill -9
"""
server_get = {"status":False,"data":""}
handler = None

class EchoHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        global server_get
        data = self.recv(1024)
        if data:
            self.send(data)
            str_data = data.decode("utf8")
            print("Client: " + str_data,self.data)
            if (server_get["status"] == False):
                server_get["status"] = True
                server_get["data"]=str_data

    def sendData(self,data):
        self.send(data.encode())

    def handle_close(self):
        self.close()
        print("CLOSE")

class EchoServer(asyncore.dispatcher):
    
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
            handler = EchoHandler(sock)


class AsyncoreRunner(threading.Thread):
    def __init__(self):
        self.server = EchoServer('0.0.0.0', 8080)
        threading.Thread.__init__(self)

    def ping(self):
        pass

    def run(self):
        print (' thread start')
        asyncore.loop()
        print (' thread stop')

    def close(self):
        self.server.close()
        self.join()


class Linuxcnc_cmd(threading.Thread):
    
    def __init__(self):
        
        self.bien =0
        threading.Thread.__init__(self)

    def run(self):
        global handler
        global server_get
        while (1):
            self.bien =self.bien +1
            if (server_get["status"]  == True):
                print("havevari ",server_get["data"] )
                server_get["status"] = False
                if handler == None:
                    continue
                handler.sendData("fffffffffff")





if __name__ == '__main__':
    ar = AsyncoreRunner()
    ar.daemon = True
    ar.start()
    li = Linuxcnc_cmd()
    li.daemon = True
    li.start()
    def exit_handler():
        #TCP_Server.stop()
        print('My application is ending!')
        #h.exit()
    atexit.register(exit_handler)
    while(1):
        #asyncore.loop(timeout=1, count=1)
        #print("S")
        time.sleep(1)
    #TCP_Server.start()