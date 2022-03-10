try: 
    import queue
except ImportError: #py2
    import Queue as queue

def init():
    global queueVNPAY
    queueVNPAY = queue.Queue(5)