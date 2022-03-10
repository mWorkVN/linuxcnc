
import os
import psutil
import time

class checkSys():
    def __init__(self):
        self.cpu = ''
        self.freemem = ''

    def run(self):
        timebg = time.time()
        total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
        self.freemem  = round((used_memory/total_memory) * 100, 2)
        return self.freemem


if __name__ == '__main__':
    app = checkSys()
    app.run()
