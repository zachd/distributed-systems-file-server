import sys
import config
from TcpServer import TcpServer

class DirectoryServer(TcpServer):
    messages = {config.REQUEST_FILE_ID, config.RETURN_FILE_ID, config.FILE_NOT_FOUND}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        # requesting file id from directory listing
        if request == config.REQUEST_FILE_ID:
            try:

                # check if folder exists in directory file system
                if vars[1] not in self.files and vars[2] == 'WRITE':
                    self.files[vars[1]] = {}

                # check if file exists in folder
                if vars[0] not in self.files[vars[1]]:
                    # save file id to directory file system
                    self.files[vars[1]][vars[0]] = {'id' : TcpServer.hash_str(vars[1] + vars[0])}
                
                # return file id and location
                self.send_msg(conn, config.RETURN_FILE_ID.format(self.files[vars[1]][vars[0]]['id']))
            
            except KeyError:
                # return file not found if file_id key not in files dict
                self.send_msg(conn, config.FILE_NOT_FOUND.format(vars[0], vars[1]))

def main():
    server = DirectoryServer(config.DIR_SERVER)
if __name__ == "__main__": main()