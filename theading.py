import threading
import logging
import time
from concurrent.futures import ThreadPoolExecutor

class ThreadLogger:
    def __init__(self, filename='log.txt'):
        self.number =0
        self.lock = threading.Lock()
        self.filename = filename
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler(self.filename), logging.StreamHandler()])

    def increment_and_log(self, thread_name):
          #with self.lock:
       
                for i in range(2):
                    self.number += 1
                    logging.info(f'Thread {thread_name}: incremented number to {self.number}')
                #  self.save_number()

    def run_thread(self, thread_name):
        logging.info(f'Thread {thread_name} started')
        self.increment_and_log(thread_name)
        logging.info(f'Thread {thread_name} finished')

def start_threads(num_threads):
    # logger = ThreadLogger(0)

    threads = []
    for i in range(num_threads):
        logger = ThreadLogger()
        thread = threading.Thread(target=logger.run_thread, args=(f'Thread-{i+1}',))
        threads.append(thread)
        thread.start()
  

        # logger=ThreadLogger()
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #      futures = [executor.submit(logger.run_thread, f'Thread-{i+1}') for i in range(num_threads)]
        #    future.result()  # Wait for the thread to complete




if __name__ == '__main__':
    start_threads(10)
