import re
import sys
import config
from threading import Lock
from TcpServer import TcpServer

class LockServer(TcpServer):
    messages = {config.REQUEST_LOCK, config.REQUEST_UNLOCK, config.REQUEST_USAGE}
    locks_mutex = Lock()
    locks = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        file_id = vars[0]
        client = vars[1]

        # lock request by client
        if request == config.REQUEST_LOCK:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # return failure if file is locked and lock owner is different client
                if file_id in self.locks and self.locks[file_id] != client:
                    self.send_msg(conn, config.LOCK_STATUS.format("FAILURE"))
                # otherwise okay to lock file for client and return success
                else:
                    self.locks[file_id] = client
                    self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
            finally:
                self.locks_mutex.release()

        # unlock request by client
        elif request == config.REQUEST_UNLOCK:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # unlock and return success if file is locked and owned by client
                if file_id in self.locks and self.locks[file_id] == client:
                    del self.locks[file_id]
                    self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
                # otherwise return failure
                else:
                    self.send_msg(conn, config.LOCK_STATUS.format("FAILURE"))
            finally:
                self.locks_mutex.release()

        # file usage request by client
        elif request == config.REQUEST_USAGE:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # return disallowed only if file is locked and owned by different client
                if file_id in self.locks and self.locks[file_id] != client:
                    self.send_msg(conn, config.LOCK_STATUS.format("DISALLOWED"))
                # otherwise return allowed to access file
                else:
                    self.send_msg(conn, config.LOCK_STATUS.format("ALLOWED"))
            finally:
                self.locks_mutex.release()

def main():
    server = LockServer(config.LOCK_SERVER)
if __name__ == "__main__": main()