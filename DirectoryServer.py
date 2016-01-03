import sys
import config
from TcpServer import TcpServer

class DirectoryServer(TcpServer):
    messages = {config.REQUEST_FILE_ID, config.RETURN_FILE_ID, config.FILE_NOT_FOUND}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        if request == config.REQUEST_FILE_ID:
            try:
                print self.files
                # check if folder exists in directory file system
                if vars[1] not in self.files and vars[2] == 'WRITE':
                    self.files[vars[1]] = {}
                # check if file exists in folder
                if vars[0] not in self.files[vars[1]]:
                    # TODO: get server for file
                    # save file id and file location to directory file system
                    self.files[vars[1]][vars[0]] = {'id' : TcpServer.hash_str(vars[1] + vars[0])}
                f = self.files[vars[1]][vars[0]]
                # return file id and location
                self.send_msg(conn, config.RETURN_FILE_ID.format(f['id'], f['id'], f['id']))
            except KeyError:
                self.send_msg(conn, config.FILE_NOT_FOUND.format(vars[0], vars[1]))
        elif request == config.CLIENT_READ_FILE:
            self.send_msg(conn, config.RETURN_FILE.format("x.py", "ASDFSADGAG"))

def main():
    # find port number from console arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")

    # start tcp server
    server = DirectoryServer(int(sys.argv[1]))

if __name__ == "__main__": main()