#!/usr/bin/env python3
# SocketCmd Server (asyncio)
# Copyright © 2016-2018, Chris Warrick.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import asyncio
import logging
import os
import signal
import random

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
l = logging.getLogger("socketcmd")
l.setLevel(logging.DEBUG)


class SocketCmdProtocol(asyncio.Protocol):
    """Query protocol for SocketCmd."""
    def __init__(self, loop):
        """Initialize a protocol instance."""
        self.loop = loop
        self.waiting_data = ''
        self.id = hex(id(self))

    def connection_made(self, transport):
        """Start a connection."""
        l.info("Connection from {0}".format(self.id))
        self.transport = transport

    def connection_lost(self, exc):
        """End a connection."""
        l.info("Disconnected from {0}".format(self.id))
        if exc:
            l.exception(exc)

    def data_received(self, data):
        """Handle requests."""
        asyncio.ensure_future(self.process_data(data))

    def output(self, line):
        """Write a line to the transport and stdout."""
        self.transport.write(line)
        l.info("Response sent: {0}".format(line))

    async def process_data(self, data, force_cmd=False):
        data = data.decode('utf-8')
        self.waiting_data += data

        if '\n' in self.waiting_data or force_cmd:
            data = self.waiting_data
            self.waiting_data = ''
            await self.handle_lines(data)

    def eof_received(self):
        """End the connection."""
        asyncio.ensure_future(self.handle_lines(self.waiting_data))

    async def handle_lines(self, data):
        """Handle lines of data."""
        for line in data.split("\n"):
            try:
                command, *args = line.split()
            except ValueError:
                continue
            l.info("Received request: {0} {1}".format(command, args))

            # Handle different request types.
            if command == "sleep":
                await asyncio.sleep(5)
                self.output(b"005 ZZZ\n")
                return
            elif command == "hi":
                self.output(b"000 HI\n")
                return
            if command == 'bool':
                if args == []:
                    arg = random.choice([b'true', b'false'])
                else:
                    arg = args[0].encode('utf-8')
                if arg not in [b'true', b'false']:
                    self.output(b"409 INVALID ARGUMENT\n")
                    return

                c = asyncio.create_subprocess_exec(arg)
                p = await c
                exit_code = await p.wait()
                if exit_code == 0:
                    self.output("210 OK {0}\n".format(arg).encode('utf-8'))
                    return
                else:
                    code = 410 + exit_code
                    self.output("{1} ERROR {0}\n".format(arg, code).encode('utf-8'))
                    return
            elif command == 'date':
                c = asyncio.create_subprocess_exec('date', '+%s',
                                                   stdout=asyncio.subprocess.PIPE)
                p = await c
                out, err = await p.communicate()
                self.output("220 DATE {0}".format(out.decode('utf-8')).encode('utf-8'))
            else:
                self.output(b"400 BAD COMMAND\n")
                return


def main():
    def exit_handler(*sigargs, **sigkw):
        l.info("Goodbye!")
        loop.stop()

    parser = argparse.ArgumentParser()
    parser.add_argument("socket", help="socket to use")
    parser.add_argument("--chmod", default=None, help="socket permissions")
    parser.add_argument("--uid", default=None, help="daemon uid")
    parser.add_argument("--gid", default=None, help="daemon gid")
    parser.add_argument("--suid", default=None, help="socket uid")
    parser.add_argument("--sgid", default=None, help="socket gid")
    args = parser.parse_args()
    uid = int(args.uid) if args.uid is not None else os.getuid()
    gid = int(args.gid) if args.gid is not None else os.getgid()
    suid = int(args.suid) if args.suid is not None else uid
    sgid = int(args.sgid) if args.sgid is not None else gid

    if uid != 0:
        l.debug("Running as user {0}".format(uid))
    else:
        l.debug("Running as root -- proceed with care")

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    coro = loop.create_unix_server(lambda: SocketCmdProtocol(loop), args.socket)
    server = loop.run_until_complete(coro)
    if args.chmod is not None:
        os.chmod(args.socket, int(args.chmod, 8))
        l.debug("Permissions set to to {0}".format(args.chmod))
    os.chown(args.socket, suid, sgid)
    l.debug("Set socket owner to {0}/{1}".format(suid, sgid))
    os.setgid(gid)
    os.setuid(uid)
    l.debug("Set process to {0}/{1}".format(uid, gid))
    l.info("Server running on {0}".format(args.socket))

    loop.add_signal_handler(signal.SIGINT, exit_handler)
    loop.add_signal_handler(signal.SIGTERM, exit_handler)

    try:
        loop.run_forever()
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
        os.remove(args.socket)


if __name__ == "__main__":
    exit(main())
