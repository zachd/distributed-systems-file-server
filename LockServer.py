import re
import sys
import config
from threading import Lock
from TcpServer import TcpServer

class LockServer(TcpServer):
    messages = {config.REQUEST_LOCK, config.REQUEST_UNLOCK}
    locks_mutex = Lock()
    locks = []

    # override request processing function
    def process_req(self, conn, request, vars):
        file_id = vars[0]
        if request == config.REQUEST_LOCK:
            try:
                self.locks_mutex.acquire()
                if file_id in self.locks:
                    self.send_msg(conn, config.LOCK_STATUS.format("FAILURE"))
                else:
                    self.locks.append(file_id)
                    self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
            finally:
                self.locks_mutex.release()
        elif request == config.REQUEST_UNLOCK:
            try:
                self.locks_mutex.acquire()
                if file_id in self.locks:
                    self.locks.remove(file_id)
                self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
            finally:
                self.locks_mutex.release()
        else:
            print request

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = LockServer(int(sys.argv[1]))

if __name__ == "__main__": main()