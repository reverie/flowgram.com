import os, Queue
from threading import Thread
from thread import get_ident

class QueueProcessor:
    def __init__(self):
        self.queue = Queue.Queue(0)

    def data_fetcher(self):
        while True:
            try:
                self.fetch()
            except Exception, e:
                print e
        
    def data_processor(self):
        while True:
            try:
                task = self.queue.get(True)
                self.process(task)
                self.queue.task_done()
            except Exception, e:
                print e
    
    def fetch(self):
        pass
    
    def process(self, task):
        pass
    
    def run(self):
        thread = Thread(target=self.data_fetcher)
        thread.setDaemon(True)
        thread.start()
        
        self.data_processor()
