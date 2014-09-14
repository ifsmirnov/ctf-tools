#!/usr/bin/python

import socket, sys, time, sqlite3

def LOG(msg):
    t = time.localtime()
    mtime = "%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
    print >> sys.stderr, "[reciever %s] %s" % (mtime, msg)

db_connection = sqlite3.connect("flags.db")

def insert_flag(flag):
    cursor = db_connection.cursor()
    cursor.execute(
            "SELECT FLAG FROM FLAGS WHERE FLAG == ? UNION " +
            "SELECT FLAG FROM USED  WHERE FLAG == ?", (flag, flag))
    if len(cursor.fetchall()) > 0:
#         LOG("Duplicate flag: %s" % flag)
        return False
    cursor.execute("INSERT INTO FLAGS VALUES(?, ?)",
            (flag, int(time.time()))) 
    db_connection.commit()
    LOG("Added flag: %s" % flag)
    return True;

def create_socket():
    port = 1992
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sock.bind(("", port))
            print "Reciever running on port", port
            break;
        except:
            port += 1
            
    sock.listen(1)
    return sock

def is_flag(s):
    if len(s) != 33 or s[-1] != "=":
        return False
    for i in s[:-1]:
        if i not in "abcdef1234567890":
            return False
    return True

def handle_connection(connection):
    data = connection.recv(1024)
#     LOG("Recieved data: '%s'" % data.strip())
    a = data.split()
    if len(a) == 0 or not is_flag(a[0]):
        return -1;
    return insert_flag(a[0])

sock = create_socket()
LOG("created socket")
while True:
    connection, address = sock.accept()
    LOG("Connection from %s" % str(address))
    try:
        retv = handle_connection(connection)
        if retv == 1:
            connection.send("Good flag!\n")
        elif retv == 0:
            connection.send("This flag is already presented\n")
        elif address[0] == "127.0.0.1":
            connection.send("quitting...\n")
        else:
            connection.send("Not a flag\n")
    finally:
        connection.close()

sock.close()
db_connection.close()
