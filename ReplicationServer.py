import sys
import config
from threading import Thread
from TcpServer import TcpServer

class ReplicationSlave(Thread):
    def __init__(self, port):
        print "Slave " + str(port) + " Created!"
        Thread.__init__(self)
        self.port = port
        self.daemon = True
        self.start()
    def run(self):
        ReplicationServer(self.port)

class ReplicationServer(TcpServer):
    messages = {config.REQUEST_FILE_DATA, config.UPDATE_FILE_DATA, config.DELETE_FILE_DATA}
    slaves = []
    files = {}

    # override init function to import slaves list
    def __init__(self, port, slaves=[]):
        self.slaves = slaves
        if slaves == []:
            self.is_slave = True
        TcpServer.__init__(self, port)

    # override request processing function
    def process_req(self, conn, request, vars):
        # requesting file data from replication server
        if request == config.REQUEST_FILE_DATA or request == config.UPDATE_FILE_DATA or request == config.DELETE_FILE_DATA:
            file_id = vars[0]

            # update file data if requesting file update
            if request == config.UPDATE_FILE_DATA:
                self.files[file_id] = vars[1]

                # propagate request to all slaves
                for slave in self.slaves:
                    print "PROPAGATING WRITE REQUEST TO " + str(slave)
                    self.propagate_msg(request, vars, slave, False)

            else:
                # check if file exists for read and delete
                if file_id in self.files:

                    # send back file data if requesting data
                    if request == config.REQUEST_FILE_DATA:
                        self.send_msg(conn, config.RETURN_FILE_DATA.format(self.files[file_id]))

                    # delete file from index if requesting file deletion
                    elif request == config.DELETE_FILE_DATA:
                        del self.files[file_id]
                        self.send_msg(conn, config.FILE_DELETION_SUCCESS)

                        # propagate request to all slaves
                        for slave in self.slaves:
                            print "PROPAGATING DELETE REQUEST TO  " + str(slave)
                            self.propagate_msg(request, vars, slave, False)
                # else return file not found
                else:
                    self.send_msg(conn, config.FILE_NOT_FOUND)



def main():
    slaves = []

    # initialise multiple other slave servers
    for i in range(config.REPLICATION_SERVERS):
        port = config.REP_SERVER + (i + 1)
        slaves.append(port)
        ReplicationSlave(port)

    # initialise master replication server
    print slaves
    master = ReplicationServer(config.REP_SERVER, slaves)


if __name__ == "__main__": main()