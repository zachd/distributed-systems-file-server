import socket
import sys
import config
import re
from time import sleep
from random import randrange

messages = [config.RETURN_FILE_DATA, config.RETURN_FILE_DETAILS, config.SUCCESS, config.FAILURE]

def send_req(ip, port, data):
    # connect server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port)) 
    s.settimeout(2)
    s.sendall(data)
    print "Sent: \"" + data.rstrip('\n') + "\""
    return get_req(s.recv(2048))

def get_req(msg):
    global messages
    print "Received: \"" + msg.rstrip('\n') + "\""
    matched_request = ""
    matched_vars = []
    for r in messages:
        m = re.match(r.replace("{}", "(.*)"), msg)
        if m:
            matched_request = r
            matched_vars = m.groups()
    return (matched_request, matched_vars)

# print connection instructions
print "Client Proxy Interface"
print "======================"
name = raw_input("Enter client name: ")

# get file details from directory server
(req, vars) = send_req("localhost", config.DIR_SERVER, config.REQUEST_FILE_DETAILS.format("test.txt", "Desktop", "WRITE"))
file_id = vars[0]
file_ip = vars[1]
file_port = int(vars[2])
raw_input("Press Enter to continue...\n")

# write file to server
file = open('test.txt', 'r')
send_req(file_ip, file_port, config.WRITE_FILE.format(file_id, name, file.read()))
raw_input("Press Enter to continue...\n")

# get lock on file
send_req("localhost", config.LOCK_SERVER, config.REQUEST_LOCK.format(file_id, name))
raw_input("Press Enter to continue...\n")

# read file from server
send_req(file_ip, file_port, config.READ_FILE.format(file_id, name))
raw_input("Press Enter to continue...\n")

# unlock file
send_req("localhost", config.LOCK_SERVER, config.REQUEST_UNLOCK.format(file_id, name))
raw_input("Press Enter to continue...\n")

