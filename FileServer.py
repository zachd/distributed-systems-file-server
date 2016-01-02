import re
import sys
import config
from TcpServer import TcpServer

class FileServer(TcpServer):
    requests = {config.CLIENT_REQUEST}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        if request == config.CLIENT_REQUEST:
            self.send_msg(conn, config.SERVER_RESPONSE.format("x.py", "ASDFSADGAG"))

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = FileServer(int(sys.argv[1]))

if __name__ == "__main__": main()