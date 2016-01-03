import re
import sys
import config
from time import sleep
from TcpServer import TcpServer

class FileServer(TcpServer):
    messages = {config.CLIENT_WRITE_FILE, config.CLIENT_READ_FILE, config.RETURN_FILE_ID, config.LOCK_STATUS, config.RETURN_FILE_DATA, config.FILE_NOT_FOUND}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        if request == config.CLIENT_WRITE_FILE or request == config.CLIENT_READ_FILE:
            filename = vars[0]
            directory = vars[1]
            action = 'WRITE' if request == config.CLIENT_WRITE_FILE else 'READ'
            (file_id_response, file_id_vars) = self.propagate_msg(config.REQUEST_FILE_ID, (filename, directory, action), config.DIR_SERVER)
            file_id = file_id_vars[0]
            print file_id
            if file_id_response == config.RETURN_FILE_ID:
                for i in range(config.LOCK_ATTEMPTS):
                    (lock_response, lock_vars) = self.propagate_msg(config.REQUEST_LOCK, (file_id), config.LOCK_SERVER)
                    if lock_vars[0] == 'SUCCESS':
                        if action == 'WRITE':
                            self.propagate_msg(config.REQUEST_FILE, (file_id), config.REPLICATION_SERVER)
                        else:
                            (replic_response, replic_vars) = self.propagate_msg(config.REQUEST_FILE, (file_id), config.REPLICATION_SERVER)
                            data = replic_vars[0]
                        break
                    else:
                        sleep(0.01)
                if lock_vars[0] == 'SUCCESS':
                    self.propagate_msg(config.REQUEST_UNLOCK, (file_id), config.LOCK_SERVER)
                    if action == 'WRITE':
                        self.send_msg(conn, config.SUCCESS.format("File " + filename + " written successfully."))
                    else:
                        self.send_msg(conn, config.RETURN_FILE.format(filename, directory, data))
                else:
                    self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File in use."))
            elif file_id_req == config.FILE_NOT_FOUND:
                self.send_msg(conn, config.FAILURE.format("Could not open " + filename, "File not found."))
        elif request == config.CLIENT_READ_FILE:
            pass
        else:
            print request

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = FileServer(int(sys.argv[1]))

if __name__ == "__main__": main()