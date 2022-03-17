# coding: utf8
import os,time
from gtts import gTTS
from playsound import playsound
from threading import Thread


class State:

    def scan(self):
        return self.name

    """def mprint(self,msg):
        if (os.name == 'nt'): print(msg,flush=True) # win
        elif (os.name == 'posix'): print(msg) # linux """

    #def logdata(self,level,msg):
    #    pass
    #    getattr(self.machine.my_logger,level)(msg)

    def speak1(self,msg):
        while(1):
            if (self.machine.queSpeaker.empty() == False):
                filename = "talk{}.mp3".format(str(int(time.time())))
                msg = self.machine.queSpeaker.get() 
                if (msg == "END"):continue
                """tts = gTTS(text=msg, lang='vi')
                tts.save(filename)
                audio_file =filename
                playsound(audio_file)
                os.remove(audio_file)"""
            time.sleep(1)

    def speak(self,msg):
        t = Thread(target=self.speak1, args=(msg,))
        t.setDaemon(True); 
        t.start()


# sudo apt-get install gstreamer-1.0
class test:
    import queue
    queSpeaker = queue.Queue(5)
    def speak1(self,msg):
        while (self.queSpeaker.empty() == False):
            filename = "talk{}.mp3".format(str(int(time.time())))
            msg = self.queSpeaker.get() 
            if (msg == "END"):continue
            tts = gTTS(text=msg, lang='vi')
            tts.save(filename)
            audio_file =filename
            print("PLAY ",msg)
            playsound(audio_file)
            os.remove(audio_file)

    def speak(self,msg):
        t = Thread(target=self.speak1, args=(msg,))
        t.setDaemon(True); 
        t.start()

if __name__ == '__main__':
    test = test()
    
    test.queSpeaker.put("Bạn Sẽ Mua ")
    test.speak("SD")
    time.sleep(5)