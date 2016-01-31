import sys
import config
from threading import Lock
from TcpServer import TcpServer

class LockServer(TcpServer):
    messages = {config.REQUEST_LOCK, config.REQUEST_UNLOCK, config.REQUEST_USE}
    locks_mutex = Lock()
    locks = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        filename = vars[0]
        location = vars[1]
        client = vars[2]

        # lock request
        if request == config.REQUEST_LOCK:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # return failure if file is locked and lock owner is different client
                if location in self.locks and filename in self.locks[location] and self.locks[location][filename] != client:
                    self.send_msg(conn, config.LOCK_STATUS.format("FAILURE"))
                # otherwise okay to lock file for client and return success
                else:
                    if location not in self.locks:
                        self.locks[location] = {}
                    self.locks[location][filename] = client
                    self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
            finally:
                self.locks_mutex.release()

        # unlock request
        elif request == config.REQUEST_UNLOCK:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # unlock and return success if file is locked and owned by client
                if location in self.locks and filename in self.locks[location] and self.locks[location][filename] == client:
                    del self.locks[location][file_id]
                    self.send_msg(conn, config.LOCK_STATUS.format("SUCCESS"))
                # otherwise return failure
                else:
                    self.send_msg(conn, config.LOCK_STATUS.format("FAILURE"))
            finally:
                self.locks_mutex.release()

        # usage request
        elif request == config.REQUEST_USE:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # return disallowed only if file is locked and owned by different client
                if location in self.locks and filename in self.locks[location] and self.locks[location][filename] != client:
                    self.send_msg(conn, config.LOCK_STATUS.format("DISALLOWED"))
                # otherwise return allowed to access file
                else:
                    self.send_msg(conn, config.LOCK_STATUS.format("ALLOWED"))
            finally:
                self.locks_mutex.release()

def main():
    server = LockServer(config.LOCK_SERVER)
if __name__ == "__main__": main()