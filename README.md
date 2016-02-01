Distributed Systems - Project
=====
> Student ID: f01f3533cd97ebd24e7c1b49639a2c3c2fd904c9e6a105226ecde32db16d0b10

An implementation of the smart thread pooling TCP server for distributed file storage.

Uses Directory Server, Lock Server, and Replication Servers (Masters) each with multiple redundant Replication Slaves.
An effort was made to ensure complete modularity of TcpServer.py, allowing for additional server types to be added with ease.


## Start all file servers in background
    >sh start.sh

## Begin client proxy (in separate ssh session)
    >python client.py