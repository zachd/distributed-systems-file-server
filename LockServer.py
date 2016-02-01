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
                    self.send_msg(conn, config.FAILURE.format("File locked by another client"))
                # otherwise okay to lock file for client and return success
                else:
                    if location not in self.locks:
                        self.locks[location] = {}
                    self.locks[location][filename] = client
                    self.send_msg(conn, config.SUCCESS.format("Locked"))
            finally:
                self.locks_mutex.release()

        # unlock request
        elif request == config.REQUEST_UNLOCK:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # unlock and return success if file is locked and owned by client
                if location in self.locks and filename in self.locks[location] and self.locks[location][filename] == client:
                    del self.locks[location][filename]
                    self.send_msg(conn, config.SUCCESS.format("Unlocked"))
                # otherwise return failure if file not in array
                elif location not in self.locks or filename not in self.locks[location]:
                    self.send_msg(conn, config.FAILIRE.format("File not locked"))
                # otherwise return file locked by another client
                else:
                    self.send_msg(conn, config.FAILURE.format("File locked by another client"))

            finally:
                self.locks_mutex.release()

        # usage request
        elif request == config.REQUEST_USE:
            try:
                # acquire locks mutex
                self.locks_mutex.acquire()
                # return disallowed only if file is locked and owned by different client
                if location in self.locks and filename in self.locks[location] and self.locks[location][filename] != client:
                    self.send_msg(conn, config.SUCCESS.format("Disallowed"))
                # otherwise return allowed to access file
                else:
                    self.send_msg(conn, config.FAILURE.format("Allowed"))
            finally:
                self.locks_mutex.release()

def main():
    print "Lock Server started on " + str(config.LOCK_SERVER)
    server = LockServer(config.LOCK_SERVER)
if __name__ == "__main__": main()