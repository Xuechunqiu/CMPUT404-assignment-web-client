#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # if catch error, return 500 Internal Server Error
        try:
            code = int(data.split('\r\n\r\n')[0].split()[1])
            return code
        except:
            return 500

    def get_headers(self, data):
        try:
            header = data.split("\r\n\r\n")[0]
            return header
        except:
            return ""

    def get_body(self, data):
        try:
            body = data.split("\r\n\r\n")[1]
            return body
        except:
            return ""

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse(self, url):
        # urllib.parse is OKAY for parsing URLs
        o = urllib.parse.urlparse(url)
        host, port = o.hostname, o.port
        # 80 for http, 443 for https
        if port == None:
            if o.scheme == 'https':
                port = 443
            else:
                port = 80
        path = "/" if o.path == "" else o.path

        return host, port, path

    # Implement basic HTTP GET
    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.parse(url)
        # print("----GET url", url, host, port, path)
        self.connect(host, port)

        request = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(
            path, host)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    # Implement basic HTTP POST
    def POST(self, url, args=None):
        code = 500
        host, port, path = self.parse(url)

        self.connect(host, port)

        # check body
        # HTTP POST can post vars
        body = ""
        if args == None:
            contentLen = 0
        else:
            for x in args:
                body += x + "=" + args[x] + "&"
            contentLen = len(body[:-1])
        # HTTP POST handles at least Content-Type: application/x-www-form-urlencoded
        request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n".format(
            path, host, str(contentLen))
        request += body[:-1]

        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
