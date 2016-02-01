# start all servers
python DirectoryServer.py &
python LockServer.py &
python ReplicationServer.py 8003 &
python ReplicationServer.py 8009 &
