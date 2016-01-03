# servers
FILE_SERVER = 8000
DIR_SERVER = 8001
REP_SERVER = 8002
LOCK_SERVER = 8003

# server messages
CLIENT_WRITE_FILE = 'WRITE_FILE: {}\nDIRECTORY: {}\nDATA: {}\n\n'
CLIENT_READ_FILE = 'READ_FILE: {}\nDIRECTORY: {}\nDATA: {}\n\n'
REQUEST_FILE_ID = 'REQUEST_FILE_ID: {}\nDIRECTORY: {}\nFUNCTION: {}\n\n'
RETURN_FILE_ID = 'FILE_ID: {}\nSERVER_IP: {}\nSERVER_PORT:\n\n'
FILE_NOT_FOUND = 'FILE_NOT_FOUND: {}\n DIRECTORY: {}\n\n'
UPDATE_FILE = 'FILE_NAME: {}\nDIRECTORY: {}\nDATA: {}\n\n'
REMOVE_FILE = 'FILE_NAME: {}\nDIRECTORY: {}\n\n'
SUCCESS = 'SUCCESS: {}\n\n'
FAILURE = 'FAILURE: {}\nREASON: {}\n\n'
RETURN_FILE = 'FILE_NAME: {}\nDATA: {}\n\n'
ERROR_MSG = 'ERROR: {}\n\n'