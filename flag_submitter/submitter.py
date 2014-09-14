#!/usr/bin/python

import zio, sys, sqlite3, time


# Verdicts
ACCEPTED = 1
NO_FLAG = 2
YOUR_FLAG = 3
DUPLICATE = 4
EXPIRED = 5
SERVICE_DOWN = 6
ERROR = 7

VERDICT_MESSAGES = (
    (ACCEPTED,      "Flag accepted"),
    (NO_FLAG,       "No flag"),
    (YOUR_FLAG,     "This is your flag"),
    (DUPLICATE,     "Flag already submitted"),
    (EXPIRED,       "Flag expired"),
    (SERVICE_DOWN,  "You cannot attack another team service if yours is down"),
    (ERROR,         ""),
)

VERDICT_SYMBOL = {
    ACCEPTED : "+",
    NO_FLAG : "-",
    YOUR_FLAG : "M",
    DUPLICATE : "D",
    EXPIRED : "E",
    SERVICE_DOWN : "W",
    ERROR : "?",
}


# Logging
from logger import Logger
log = Logger("submitter")


# Connections
db_connection = sqlite3.connect("flags.db")
HOST = "127.0.0.1"
PORT = 9000


# Preparation
# Create tables in db if not yet created


def submit_flag(flag):
    # flags are now submitted using one connection per flag
    # whilst testing systems allow submitting multiple flags
    # during one connection. TODO
    log.debug("Submitting flag %s", flag)
    try_number = 0
    while True:
        try_number += 1
        try:
            connection = zio.zio(
                    (HOST, PORT), print_read=False, print_write=False)
            break
        except:
            log.debug("Unsuccessful connection attempt")
            if try_number % 10 == 0:
                log.error("%d unsuccessful connections in a row", try_number)
            time.sleep(0.3)

    connection.read_line() # jury greeting
    connection.write(flag + "\n")
    response = connection.read().strip()
    connection.close()

    log.debug("Response for %s: '%s'", flag, response)

    for verdict, message in VERDICT_MESSAGES:
        if message in response:
            return verdict

def submit_all():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM FLAGS ORDER BY TIMESTAMP")
    flags = cursor.fetchall()
    if len(flags) == 0:
        log.debug("submitted 0 flags")
        return

    verdicts_count = {}

    for verdict, _ in VERDICT_MESSAGES:
        verdicts_count[verdict] = 0

    for flag, timestamp in flags:
        ret = submit_flag(flag)

        if ret == ERROR:
            log.error("Strange error for flag %s", flag)
        verdicts_count[ret] += 1

        if ret in (SERVICE_DOWN, ERROR):
            cursor.execute("DELETE FROM FLAGS WHERE FLAG == ?", (flag,))
            cursor.execute("INSERT INTO FLAGS VALUES (?,?)",
                    (flag, int(timestamp) + 60 * 1))
            db_connection.commit()
        else:
            cursor.execute("INSERT INTO USED VALUES (?)", (flag,))
            cursor.execute("DELETE FROM FLAGS WHERE FLAG == ?", (flag,))
            db_connection.commit()

    status = "Submitted %d ="
    for verdict, _ in VERDICT_MESSAGES:
        status += " "
        status += VERDICT_SYMBOL[verdict]
        status += str(verdicts_count[verdict])
    log.info(status, len(flags))

while True:
    submit_all()
    time.sleep(1)

