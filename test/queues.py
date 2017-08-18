from queue import Queue
from threading import Thread
import time

q = Queue()

def producer():
    global q
    while True:
        q.put('fun')
        q.put('times')
        q.put('now')
        time.sleep(1)

def consumer():
    while True:
        data = q.get()
        print("got data", data)

produce_thread = Thread(target=producer, args=())
consume_thread = Thread(target=consumer, args=())

produce_thread.start()
consume_thread.start()
