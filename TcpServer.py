import sys
import socket
import re
import os
import math
import config
import hashlib
from time import sleep
from Queue import Queue
import thread
from threading import Thread, Lock

# define worker class that implements thread
# base from http://code.activestate.com/recipes/577187-python-thread-pool/
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, requests, server):
        Thread.__init__(self)
        # store clients queue pointer
        self.requests = requests
        # pointer to master server object
        self.server = server
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
                for msg in self.server.extract_msg(conn, addr):
                    (request, vars) = self.server.get_req(conn, msg)
                    self.server.process_req(conn, request, vars)
            else:
                break;
            # set task as done in queue
            self.requests.task_done()

# define main tcp server class
class TcpServer(object):

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
        self.requests = Queue()

        # thread counter
        self.num_threads = self.MIN_THREADS

        # bind to port and listen for connections
        s.bind(("0.0.0.0", port)) 
        (self.ip, self.port) = s.getsockname()
        s.listen(5)

        # create initial workers
        for _ in range(int(self.MIN_THREADS)): 
            Worker(self.requests, self)

        # continuous loop to keep accepting requests
        while 1:
            # accept a connection request
            conn, addr = s.accept()
            self.accept(conn, addr)

    # accept connection request from socket
    def accept(self, conn, addr):
        # cache queue size and get threshold
        qsize = self.requests.qsize()
        queue_margin = int(math.ceil(self.num_threads * (self.QUEUE_THRESHOLD / 100.0)))

        # check if queue size is between num_threads and (num_threads - margin)
        if qsize >= (self.num_threads - queue_margin) and self.num_threads != self.MAX_THREADS:
            # add queue_margin amount of new workers
            for _ in range(queue_margin): 
                if self.num_threads == self.MAX_THREADS:
                    break
                Worker(self.requests)
                self.num_threads += 1
        # else check if queue size is between 0 and margin
        elif qsize <= queue_margin and self.num_threads != self.MIN_THREADS:
            # remove queue_margin amount of workers
            for _ in range(queue_margin): 
                if self.num_threads == self.MIN_THREADS:
                    break
                clients.put((None, None))
                self.num_threads -= 1

        # receive data and put request in queue
        self.requests.put((conn, addr))
    
    # create hash of string
    def hash_str(self, string):
        sha = hashlib.sha1(string)
        return sha.hexdigest()

    # function to get message text from a connection
    def extract_msg(self, conn, addr):
        while conn:
            msg = ""
            # Loop through message to receive data
            while "\n\n" not in msg and conn:
                data = conn.recv(4096)
                msg += data
                if len(data) < 4096:
                    break
            # yields current msg from conn if found
            if msg:
                yield msg
                # break if not client connecting file server
                if self.port != config.FILE_SERVER:
                    break

    # send message back to connection
    def send_msg(self, conn, data):
        # supress replication server messages
        if not hasattr(self, 'is_slave') or self.is_slave == False:
            print "Sent: \"" + data.rstrip('\n') + "\""
        conn.sendall(data)

    # read the request message from the input
    def get_req(self, conn, msg):
        # supress replication server messages
        if not hasattr(self, 'is_slave') or self.is_slave == False:
            print "Received: \"" + msg.rstrip('\n') + "\""
        matched_request = ""
        matched_vars = []
        for r in self.messages:
            m = re.match(r.replace("{}", "(.*)"), msg)
            if m:
                matched_request = r
                matched_vars = m.groups()
        if not matched_request:
            self.error(conn, "Unknown Message")
        else:
            return (matched_request, matched_vars)

    # send message to server
    def propagate_msg(self, request, vars, server, response_required=True):
        # connect to socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", server)) 

        # send data
        self.send_msg(s, request.format(*vars))

        # accept response from socket
        if response_required:
            for msg in self.extract_msg(s, s.getpeername()):
                s.close()
                return self.get_req(s, msg)

    # return an error message to the user
    def error(self, conn, msg):
        self.send_msg(conn, config.ERROR_MSG.format(msg))