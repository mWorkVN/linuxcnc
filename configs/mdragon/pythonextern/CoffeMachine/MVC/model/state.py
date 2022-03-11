# coding: utf8
import os,time
from gtts import gTTS
from playsound import playsound
from threading import Thread


class State:

    def scan(self):
        return self.name

    def mprint(self,msg):
        if (os.name == 'nt'): print(msg,flush=True) # win
        elif (os.name == 'posix'): print(msg) # linux 

    def logdata(self,level,msg):
        pass
        getattr(self.machine.my_logger,level)(msg)

    def speak1(self,msg):
        while(1):
            if (self.machine.Que.empty() == False):
                filename = "talk{}.mp3".format(str(int(time.time())))
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
