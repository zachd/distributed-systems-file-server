import socket
import sys
import config
import re
from time import sleep
from random import randrange

messages = [config.RETURN_FILE_DETAILS]

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


# connect to directory server
ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ds.connect(("localhost", config.DIR_SERVER)) 
ds.settimeout(2)

# get location of file to write
data = config.REQUEST_FILE_DETAILS.format("test.txt", "Desktop", "WRITE")
print "Sent: \"" + data + "\""
ds.sendall(data)
(req, vars) = get_req(ds.recv(2048))
file_id = vars[0]
file_ip = vars[1]
file_port = vars[2]
raw_input("Press Enter to continue...")


# connect to file server
fs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fs.connect((vars[1], int(vars[2])))
fs.settimeout(2)

# write file to 
file = open('test.txt', 'r')
data = config.WRITE_FILE.format("test.txt", "Desktop", name, file.read())
print "Sent: \"" + data + "\""
fs.sendall(data)

# print received response
(req, vars) = get_req(fs.recv(2048))
raw_input("Press Enter to continue...")
