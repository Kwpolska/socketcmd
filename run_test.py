#!/usr/bin/env python3
"""Run a “test suite” for socketcmd."""
import subprocess
import sys
import time


def ael(l, c):
    """assertEqual line-wise"""
    if client_out[l] != c:
        print("\033[1;31mFAIL\033[0m on line {0}".format(l))
        print("Expected:", repr(c))
        print("Found:   ", repr(client_out[l]))
        sys.exit(1)


def aelin(l, cs):
    "assertEqual line-wise in"""
    if client_out[l] not in cs:
        print("\033[1;31mFAIL\033[0m on line {0}".format(l))
        print("Expected:", repr(cs))
        print("Found:   ", repr(client_out[l]))
        sys.exit(1)


print("Starting test session...")
server = subprocess.Popen([sys.executable, 'socketcmd_server.py', 'sc.sock'])
time.sleep(1)  # initialization

try:
    client = subprocess.run([sys.executable, 'socketcmd_client_demo.py', 'sc.sock'],
                            capture_output=True, timeout=15, encoding='utf-8')
except subprocess.TimeoutExpired as e:
    print("\033[1;31mFAIL (TIMEOUT)\033[0m")
    print(e)
    sys.exit(2)

client_out = client.stdout.split('\n')
print(client.stdout)


ael(0, "Connecting to sc.sock.")
ael(1, "<<< hi")
ael(2, "000 HI")
ael(3, "<<< bool")
aelin(4, ("411 ERROR b'false'", "210 OK b'true'"))
ael(5, "<<< bool")
aelin(6, ("411 ERROR b'false'", "210 OK b'true'"))
ael(7, "<<< bool true")
ael(8, "210 OK b'true'")
ael(9, "<<< bool false")
ael(10, "411 ERROR b'false'")
ael(11, "<<< date")
# answer 1
ael(13, "<<< sleep")
ael(14, "005 ZZZ")
ael(15, "<<< date")
# answer 2
ael(17, "Disconnecting.")

date1, date2 = client_out[12], client_out[16]
if date1[:9] != date2[:9]:
    print("\033[1;31mFAIL\033[0m, date lines mismatch")
    print(repr(date1))
    print(repr(date2))
    sys.exit(3)
t1 = int(date1.split(' ')[-1])
t2 = int(date2.split(' ')[-1])
difference = t2 - t1
if difference not in {4, 5, 6}:
    print("\033[1;31mFAIL\033[0m, date lines are not within {4, 5, 6}")
    print(repr(date1))
    print(repr(date2))
    print('{t2} - {t1} = {difference}'.format(t2=t2, t1=t1, difference=difference))
    sys.exit(4)

server.kill()
print("\033[1;32mPASS\033[0m")
