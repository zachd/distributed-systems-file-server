import sys
import socket
import re
import os
import math
from time import sleep
from Queue import Queue
import thread
from threading import Thread, Lock

# define worker class that implements thread
# base from http://code.activestate.com/recipes/577187-python-thread-pool/
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, requests, func):
        print "Worker Created!"
        Thread.__init__(self)
        # store clients queue pointer
        self.requests = requests
        # outer function to process request
        self.func = func
        # set as daemon so it dies when main thread exits
        self.daemon = True
        # start the thread on init
        self.start()

    # function run indefinitely once thread is started
    def run(self):
        while True:
            # pop an element from the queue
            (conn, addr) = self.requests.get()
            # check if valid connection or else kill loop
            if conn:
                self.get_msg(conn, addr)
            else:
                break;
            # set task as done in queue
            self.requests.task_done()

    # function to get message text from a connection
    def get_msg(self, conn, addr):
        while conn:
            msg = ""
            # Loop through message to receive data
            while "\n\n" not in msg:
                data = conn.recv(4096)
                msg += data
                if len(data) < 4096:
                    break
            # pass message to TcpServer process_req function
            if msg:
                self.func(msg)

# define main tcp server class
class TcpServer():

    # queue threshold to increase or decrease num workers
    QUEUE_THRESHOLD = 50.0

    # max and min number of threads
    MAX_THREADS = 100.0
    MIN_THREADS = 10.0

    def __init__(self, port):
        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # queue object to store requests
        requests = Queue()

        # thread counter
        num_threads = self.MIN_THREADS

        # bind to port and listen for connections
        s.bind(("0.0.0.0", port)) 
        s.listen(5)

        # create initial workers
        for _ in range(int(self.MIN_THREADS)): 
            Worker(requests, self.process_req)

        # continuous loop to keep accepting requests
        while 1:
            # accept a connection request
            conn, addr = s.accept()

            # cache queue size and get threshold
            qsize = requests.qsize()
            queue_margin = int(math.ceil(num_threads * (self.QUEUE_THRESHOLD / 100.0)))

            # check if queue size is between num_threads and (num_threads - margin)
            if qsize >= (num_threads - queue_margin) and num_threads != self.MAX_THREADS:
                # add queue_margin amount of new workers
                for _ in range(queue_margin): 
                    if num_threads == self.MAX_THREADS:
                        break
                    Worker(requests)
                    num_threads += 1
            # else check if queue size is between 0 and margin
            elif qsize <= queue_margin and num_threads != self.MIN_THREADS:
                # remove queue_margin amount of workers
                for _ in range(queue_margin): 
                    if num_threads == self.MIN_THREADS:
                        break
                    clients.put((None, None))
                    num_threads -= 1

            # receive data and put request in queue
            requests.put((conn, addr))

    # function to process request from worker thread
    def process_req(self, msg):
        print "Received Request: " + msg

def main():
    
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = TcpServer(int(sys.argv[1]))

if __name__ == "__main__": main()