import time
import datetime
import redis
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from queue import Queue
from threading import Thread
import os
from watchdog.events import FileCreatedEvent
import remove_older
import sender
import verifier
import dot_finder
import elogger

dir_path = r"/home/tzur/all-the-photos"


def process_queue(q):
    counter = 0
    half_two_arr = []
    half_one_arr = []
    while True:
     #   time.sleep(1)
        counter += 1

        half_one_arr = remove_older.remove(half_one_arr)
        half_two_arr = remove_older.remove(half_two_arr)
        if not q.empty():
            event = q.get()
            dot = dot_finder.find(event.src_path)

            if not event.src_path in used_arr:
                elogger.write("arrivedtoserver")

            if event.src_path[:dot][-1] != "a" and event.src_path[:dot][-1] != "b":
     #           print("irrelevant")
                os.remove(event.src_path)
                continue

            elif event.src_path[:dot][-1] == "a":
      #          print("first half – adding")
                r.set(f"{event.src_path[:dot - 2]}", event.src_path)
                #change now with os.path.getctime(i[0]) to get the exact time
                half_one_arr.append((event.src_path, datetime.datetime.utcnow()))
                # if len(half_two_arr) > 0:
                #     is_valid = verifier.verify(half_one_arr, half_two_arr)
                #     if is_valid:
                #         sender.send(event.src_path)

            elif event.src_path[:dot][-1] == "b":
       #         print("only second half – appending")
                half_two_arr.append((event.src_path, datetime.datetime.utcnow()))
                if len(half_one_arr) > 0:
                    is_valid = verifier.verify(half_one_arr, half_two_arr)
                    if is_valid:
                        sender.send(event.src_path)
                    else:
                        for i in half_two_arr:
                            if i[0] == event.src_path:
                                half_two_arr.remove(i)
                                os.remove(event.src_path)
        #                        print("too many time has passed")


class FileWatchdog(PatternMatchingEventHandler):
    def __init__(self, queue, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=["*"], ignore_patterns=None, ignore_directories=False,
                                             case_sensitive=True)
        self.queue = queue

    def process(self, event):
        self.queue.put(event)

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    watchdog_queue = Queue()
    r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
    used_arr = []

    for file in os.listdir(dir_path):
        filename = os.path.join(dir_path, file)
        used_arr.append(filename)
        event = FileCreatedEvent(filename)
        watchdog_queue.put(event)

    worker = Thread(target=process_queue, args=(watchdog_queue,), daemon=True)
    worker.start()
    event_handler = FileWatchdog(watchdog_queue, patterns="*.ini")
    observer = Observer()
    observer.schedule(event_handler, path=dir_path)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
