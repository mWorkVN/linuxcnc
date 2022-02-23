# coding: utf8
import sys, time ,os
#import logging
#import logging.handlers
from gtts import gTTS
from playsound import playsound
import pyttsx3
from threading import Thread

"""try: 
    import queue
except ImportError: #py2
    import Queue as queue
import imp
"""
class State:

    def scan(self):
        #self.mprint("Current Name State  " + self.name)
        return self.name
        pass

    def mprint(self,msg):
        if (os.name == 'nt'): print(msg,flush=True) # win
        elif (os.name == 'posix'): print(msg) # linux 

    def logdata(self,level,msg):
        pass
        getattr(self.machine.my_logger,level)(msg)

    def speak1(self,msg):
        while(1):
            if (self.machine.Que.empty() == False):
                filename = "talk"+str(int(time.time()))+".mp3"
                msg = self.machine.Que.get() 
                if (msg == "END"):continue
                print("Play ",str(filename),flush=True)
                #tts = gTTS(text=msg, lang='vi')
                #tts.save(filename)
                #audio_file =filename
                #playsound(audio_file)
                #os.remove(audio_file)

    def speak(self,msg):
        t = Thread(target=self.speak1, args=(msg,))
        t.setDaemon(True); 
        t.start()
