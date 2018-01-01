SocketCmd
=========

SocketCmd is a Unix domain socket-based server that runs selected shell
commands (or anything else, really). The server is built in Python 3, using
[`asyncio`](https://docs.python.org/3/library/asyncio.html). There is also a
small demo client using the `socket` library — but `netcat -U` is also a good
interface.

This is a censored version of a slightly different project with internal
references, original names and real purpose removed for security reasons.
The real project runs on my web server and communicates with a Django web
application. SocketCmd is meant to show how a socket server that runs
subprocesses looks when written in asyncio.

Usage
-----

Basic usage:

    ./socketcmd_server.py socketcmd.sock

Client:

    ./socketcmd_client_demo.py socketcmd.sock
    netcat -U socketcmd.sock

Special usage: see `./socketcmd_server.py --help` for full argument list,
including a choice of socket permissions (requires starting as root) and
process permissions (requires setuid/setgid bits for the executable:
`chmod ug+s socketcmd_server.py`)

Default commands
----------------

Commands and responses must end with a new line.

* `hi` — immediately responds with `000 HI`
* `sleep` — responds with `005 ZZZ` after 5 seconds. (Does not block!)
* `bool [true|false]` — responds with either `210 OK b'true'` or `411 ERROR
  b'false'` depending on the parameter or random chance if omitted
* `date` — responds with `220 DATE xxx`, where `xxx` is seconds since 1970
  (Unix timestamp)

Any other command responds with `400 BAD COMMAND`. Commands are case sensitive.

License
-------

Copyright © 2016-2018, Chris Warrick.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions, and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions, and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the author of this software nor the names of
   contributors to this software may be used to endorse or promote
   products derived from this software without specific prior written
   consent.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
