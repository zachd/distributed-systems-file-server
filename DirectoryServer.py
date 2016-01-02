import sys
import config
from TcpServer import TcpServer

class DirectoryServer(TcpServer):
    def process_req(self, msg):
        print "Testing" + msg

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = DirectoryServer(int(sys.argv[1]))

if __name__ == "__main__": main()