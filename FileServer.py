import re
import sys
import config
from TcpServer import TcpServer

class FileServer(TcpServer):
    messages = {config.CLIENT_WRITE_FILE, config.CLIENT_READ_FILE, config.RETURN_FILE_ID, config.FILE_NOT_FOUND}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        if request == config.CLIENT_WRITE_FILE:
            (file_id_req, file_id_vars) = self.propagate_msg(config.REQUEST_FILE_ID, (vars[0], vars[1], 'WRITE'), config.DIR_SERVER)
            if file_id_req == config.RETURN_FILE_ID:
                print "FILE ID:" + str(file_id_vars[0])
            #self.send_msg(conn, config.SUCCESS.format("File " + vars[0] + " was uploaded."))
        elif request == config.CLIENT_READ_FILE:
            self.send_msg(conn, config.RETURN_FILE.format("x.py", "ASDFSADGAG"))
        else:
            print request

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = FileServer(int(sys.argv[1]))

if __name__ == "__main__": main()