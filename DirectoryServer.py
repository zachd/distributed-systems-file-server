import sys
import config
import random
from TcpServer import TcpServer

class DirectoryServer(TcpServer):
    messages = {config.REQUEST_FILE_DETAILS}
    servers = [config.REP_SERVER + (x * (config.REP_SERVER_COPIES + 1)) for x in range(config.REP_SERVERS)]
    folders = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        # requesting file details from directory
        if request == config.REQUEST_FILE_DETAILS:
            try:
                # add folder to directory listing if writing
                if vars[2] == 'WRITE':
                    # check if folder exists in directory listing
                    if vars[1] not in self.folders:
                        # if not then assign folder to random server
                        random_server_port = random.choice(self.servers)
                        self.folders[vars[1]] = {'id' : self.hash_str(self.ip + str(random_server_port) + vars[1]), 'ip' : self.ip, 'port' : str(random_server_port), 'files' : [vars[0]]}
                
                # return directory id and location
                response = self.folders[vars[1]]

                # check if file in directory
                if vars[0] in response['files']:
                    self.send_msg(conn, config.RETURN_FILE_DETAILS.format(response['id'], response['ip'], response['port']))
                else:
                    self.error(conn, "File not found.")
            
            except KeyError:
                # return file not found if file_id key not in files dict
                self.error(conn, "File not found.")

def main():
    server = DirectoryServer(config.DIR_SERVER)
if __name__ == "__main__": main()