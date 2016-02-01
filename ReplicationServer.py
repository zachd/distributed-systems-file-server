import os
import sys
import config
from threading import Thread
from TcpServer import TcpServer

class ReplicationSlave(Thread):
    def __init__(self, port):
        print "Replication Slave " + str(port) + " Created!"
        Thread.__init__(self)
        self.port = port
        self.daemon = True
        self.start()
    def run(self):
        ReplicationServer(self.port)

class ReplicationServer(TcpServer):
    messages = {config.READ_FILE, config.WRITE_FILE, config.DELETE_FILE}
    slaves = []
    files = {}

    # override init function to import slaves list
    def __init__(self, port, slaves=[]):
        self.slaves = slaves
        if slaves == []:
            self.is_slave = True
        if not os.path.exists(str(port)):
            os.makedirs(str(port))
        TcpServer.__init__(self, port)

    # override request processing function
    def process_req(self, conn, request, vars):
        # requesting file data from replication server
        if request == config.READ_FILE or request == config.WRITE_FILE or request == config.DELETE_FILE:
            filename = vars[0]
            location = vars[1]

            # update file data if requesting file update
            if request == config.WRITE_FILE:
                data = vars[3]
                if location not in self.files:
                    self.files[location] = {}

                self.files[location][filename] = True

                # write file to disk
                f = open(os.path.join(str(self.port), filename), 'w')
                f.write(data)
                f.close()

                # propagate request to all slaves if master
                for slave in self.slaves:
                    print "PROPAGATING WRITE REQUEST TO " + str(slave)
                    self.propagate_msg(request, vars, slave, False)

                # respond to client with success message
                if self.slaves:
                    self.send_msg(conn, config.SUCCESS.format("File " + filename + " written."))
            else:
                # check if file exists for read and delete
                if location in self.files and filename in self.files[location]:

                    # send back file data if requesting data
                    if request == config.READ_FILE:
                        f = open(os.path.join(str(self.port), filename), 'r')
                        self.send_msg(conn, config.RETURN_FILE_DATA.format(f.read()))
                        f.close()

                    # delete file from index if requesting file deletion
                    elif request == config.DELETE_FILE:
                        del self.files[file_id]
                        self.success(conn, "File deletion success.")

                        # propagate request to all slaves
                        for slave in self.slaves:
                            print "PROPAGATING DELETE REQUEST TO  " + str(slave)
                            self.propagate_msg(request, vars, slave, False)

                # else return file not found
                else:
                    self.error(conn, "File not found.")

def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")
    print "Replication Master started on " + sys.argv[1]
    
    slaves = []

    # initialise multiple other slave servers
    for i in range(config.REP_SERVER_COPIES):
        port = int(sys.argv[1]) + (i + 1)
        slaves.append(port)
        ReplicationSlave(port)

    # initialise master replication server
    master = ReplicationServer(int(sys.argv[1]), slaves)


if __name__ == "__main__": main()