#!/usr/bin/python

import zio, sys, sqlite3, time

def LOG(msg):
    t = time.localtime()
    mtime = "%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
    print >> sys.stderr, "[submitter %s] %s" % (mtime, msg)

db_connection = sqlite3.connect("flags.db")
HOST = "10.0.77.2"
PORT = 9000

AC = 1
NOT_FLAG = 2
ERROR = 3

def submit_flag(flag):
    LOG("Submitting %s" % flag)
    while True:
        try:
            connection = zio.zio(
                    (HOST, PORT), print_read=False, print_write=False)
            break
        except:
            LOG("Unsuccessful connection attempt")
            time.sleep(0.3)

    connection.read_line()
    connection.write(flag + "\n")
    data = connection.read().strip()
    connection.close()
    LOG("Msg for '%s': '%s'" % (flag, data))
    if data in (
            'No flag',
            'This is your flag',
            'Flag expired',
            'Flag already submitted'):
        return NOT_FLAG
    if data == "Flag accepted":
        return AC
    return ERROR

def submit_all():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM FLAGS ORDER BY TIMESTAMP")
    flags = cursor.fetchall()
    for i in flags:
        ret = submit_flag(i[0])
        if ret in (AC, NOT_FLAG):
            LOG("Flag %s moved to used" % i[0])
            cursor.execute("INSERT INTO USED VALUES (?)", (i[0],))
            cursor.execute("DELETE FROM FLAGS WHERE FLAG == ?", (i[0],))
            db_connection.commit()
        else:
            LOG("Flag %s delayed" % i[0])
            cursor.execute("DELETE FROM FLAGS WHERE FLAG == ?", (i[0],))
            cursor.execute("INSERT INTO FLAGS VALUES (?,?)",
                    (i[0], int(i[1]) + 60 * 1))
            db_connection.commit()
    LOG("Submitted %d flags" % len(flags))

while True:
    submit_all()
    time.sleep(1)

