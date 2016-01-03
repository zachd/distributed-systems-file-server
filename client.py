import socket
import sys
import config
from time import sleep
from random import randrange

if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    sys.exit("Port number required")

# connect to socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", int(sys.argv[1]))) 
s.settimeout(2)

# send data
data = config.CLIENT_WRITE_FILE.format("test.py", "Desktop", "hello")
print "Sent: \"" + data + "\""
s.sendall(data)

# print received response
received = s.recv(2048)
print "Received: \"{}\"".format(received)