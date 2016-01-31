# servers
FILE_SERVER = 8000
DIR_SERVER = 8001
LOCK_SERVER = 8002
REP_SERVER = 8003

# variables
LOCK_ATTEMPTS = 1
REP_SERVERS = 1
REP_SERVER_COPIES = 5

# client and directory server communication
REQUEST_FILE_DETAILS = 'REQUEST_FILE_DETAILS: {}\nDIRECTORY: {}\nACTION: {}\n\n'
RETURN_FILE_DETAILS = 'RETURN_FILE_DETAILS: {}\nIP: {}\nPORT: {}\n\n'

# client/replication server and lock server communication
REQUEST_LOCK = 'REQUEST_LOCK: {}\nLOCATION: {}\nCLIENT: {}\n\n'
REQUEST_USE = 'REQUEST_USE: {}\nLOCATION: {}\nCLIENT: {}\n\n'
REQUEST_UNLOCK = 'REQUEST_UNLOCK: {}\nLOCATION: {}\nCLIENT: {}\n\n'
LOCK_STATUS = 'LOCK_STATUS: {}\n\n'

# client and replication server communication
WRITE_FILE = 'WRITE_FILE: {}\nLOCATION: {}\nCLIENT: {}\nDATA: {}\n\n'
READ_FILE = 'READ_FILE: {}\nLOCATION: {}\nCLIENT: {}\n\n'
DELETE_FILE = 'DELETE_FILE: {}\nLOCATION: {}\nCLIENT: {}\n\n'
RETURN_FILE_DATA = 'RETURN_FILE_DATA: {}\n\n'

# status messages
SUCCESS = 'SUCCESS: {}\n\n'
FAILURE = 'FAILURE: {}\nREASON: {}\n\n'
ERROR_MSG = 'ERROR: {}\n\n'