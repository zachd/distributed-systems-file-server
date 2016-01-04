import re
import sys
import config
from time import sleep
from TcpServer import TcpServer

class FileServer(TcpServer):
    messages = {config.CLIENT_WRITE_FILE, config.CLIENT_READ_FILE, config.CLIENT_DELETE_FILE, config.RETURN_FILE_ID, config.LOCK_STATUS, config.CLIENT_REQUEST_LOCK, config.CLIENT_REQUEST_UNLOCK, config.RETURN_FILE_DATA, config.FILE_DELETION_SUCCESS, config.FILE_NOT_FOUND}
    files = {}

    # override request processing function
    def process_req(self, conn, request, vars):
        # client requesting to read or write to file
        if request == config.CLIENT_WRITE_FILE or request == config.CLIENT_READ_FILE or request == config.CLIENT_DELETE_FILE:
            filename = vars[0]
            directory = vars[1]
            client = vars[2]
            # set action keyword depending on client request
            action = request.split('_', 1)[0]

            # request file identifier from the directory server
            (file_id_response, file_id_vars) = self.propagate_msg(config.REQUEST_FILE_ID, (filename, directory, action), config.DIR_SERVER)
            if file_id_response == config.RETURN_FILE_ID:
                file_id = file_id_vars[0]

                # attempt to gain access to the file from lock server
                for i in range(config.LOCK_ATTEMPTS):
                    (lock_response, lock_vars) = self.propagate_msg(config.REQUEST_USAGE, (file_id,client), config.LOCK_SERVER)
                    
                    # check if lock server allows file usage
                    if lock_vars[0] == 'ALLOWED':
                        if action == 'WRITE':
                            # send write request to replication master to update file data
                            self.propagate_msg(config.UPDATE_FILE_DATA, (file_id, vars[3]), config.REP_SERVER, False)
                            # return success message to user
                            self.send_msg(conn, config.SUCCESS.format("File " + filename + " written successfully."))
                        elif action == 'READ':
                            # send deletion request to replication master
                            (replic_response, replic_vars) = self.propagate_msg(config.REQUEST_FILE_DATA, (file_id,), config.REP_SERVER)
                            if replic_response == config.RETURN_FILE_DATA:
                                data = replic_vars[0]
                                self.send_msg(conn, config.RETURN_FILE_DATA.format(data))
                            elif replic_response == config.FILE_NOT_FOUND:
                                self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File not found."))
                        elif action == 'DELETE':
                            # ask for file data from replication master to send back to user
                            (replic_response, replic_vars) = self.propagate_msg(config.DELETE_FILE_DATA, (file_id,), config.REP_SERVER)
                            if replic_response == config.FILE_DELETION_SUCCESS:
                                self.send_msg(conn, config.SUCCESS.format("File " + filename + " deleted successfully."))
                            elif replic_response == config.FILE_NOT_FOUND:
                                self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File not found."))
                        break
                    else:
                        # sleep and try file access again
                        sleep(0.01)

                # return failure message to user if lock server disallowed access
                if lock_vars[0] != 'ALLOWED':
                    self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File is locked."))
            
            # return failure message to user if directory server couldn't find file
            elif file_id_response == config.FILE_NOT_FOUND:
                self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File not found."))
        
        # client request to lock or unlock file
        elif request == config.CLIENT_REQUEST_LOCK or request == CLIENT_REQUEST_UNLOCK:
            filename = vars[0]
            directory = vars[1]
            client = vars[2]

            # set action request and keyword depending on client request
            desired_action = config.REQUEST_LOCK if request == config.CLIENT_REQUEST_LOCK else config.REQUEST_UNLOCK
            act_completed = "lock" if request == CLIENT_REQUEST_LOCK else "unlock"
            
            # request file identifier from the directory server
            (file_id_response, file_id_vars) = self.propagate_msg(config.REQUEST_FILE_ID, (filename, directory, "READ"), config.DIR_SERVER)
            if file_id_response == config.RETURN_FILE_ID:
                file_id = file_id_vars[0]

                # attempt to perform specified action on lock server
                for i in range(config.LOCK_ATTEMPTS):
                    (lock_response, lock_vars) = self.propagate_msg(desired_action, (file_id, client), config.LOCK_SERVER)
                    
                    # check if action completed successfully
                    if lock_vars[0] == 'SUCCESS':
                        self.send_msg(conn, config.SUCCESS.format("File " + filename + " " + act_completed + "ed successfully."))
                        break
                    else:
                        # sleep and try action again
                        sleep(0.01)

                # return failure message to user if lock server disallowed action
                if lock_vars[0] != 'SUCCESS':
                    self.send_msg(conn, config.FAILURE.format("Could not " + act_completed + " " + filename, "File locked by another user."))
            
            # return failure message to user if directory server couldn't find file
            elif file_id_response == config.FILE_NOT_FOUND:
                self.send_msg(conn, config.FAILURE.format("Could not access " + filename, "File not found."))

def main():
    server = FileServer(config.FILE_SERVER)
if __name__ == "__main__": main()