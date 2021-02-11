#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Created February 2020 by Kyle Fujishige
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
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    # split up a url and determine each of the values by looking at each part of the parsed url.
    def get_parsed_url(self,parsedUrl):
        port = 0
        host = ''
        path = ''
        query = ''
        fragment = ''
        if (parsedUrl.scheme == 'http'):
            port = 80
        elif (parsedUrl.scheme == 'https'):
            port = 443
                
        if (len(parsedUrl.netloc.split(':')) == 2):
            [host, port] = parsedUrl.netloc.split(':')
            port = int(port)
        else:
            host = parsedUrl.netloc

        if (parsedUrl.path == ''):
            path = '/'
        else:
            path = parsedUrl.path

        if (parsedUrl.query != ''):
            query = '?' + parsedUrl.query

        if (parsedUrl.fragment != ''):
            fragment = '#' + parsedUrl.fragment

        return (host, port, path, query, fragment)

    # Connect to a server
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # Get http return code
    def get_code(self, data):
        response = data.split('\r\n')[0]
        return int(response.split(' ')[1])

    # Get http return headers
    def get_headers(self,data):
        headers = []
        response = data.split('\r\n')
        for i in range(1, len(response), 1):
            if (response[i] == ''):
                break
            headers.append(response[i])
        return headers

    # Get http returned body
    def get_body(self, data):
        response = data.split('\r\n')
        headers = self.get_headers(data)
        for i in range(1, len(response), 1):
            if(response[i] not in headers and response[i] != ''):
                return response[i]
        return None
    
    # Send all the data to a server
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    # Close a socket
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
        return buffer.decode('ISO-8859-1')

    # http get command handler
    def GET(self, url, args=None):
        port = 0
        host = ''
        path = ''
        query = ''
        fragment = ''

        # Use urllib.parse to parse URL
        parsedUrl = urlparse(url)
        
        # Get all parts of the parsed url into variables
        (host, port, path, query, fragment) = self.get_parsed_url(parsedUrl)
        
        # Check to see if port and host aren't empty
        if(port != 0 and host != ''):

            # connect to server
            self.connect(host, port)
            # setup get command
            msg = 'GET ' + path + query + fragment + ' HTTP/1.1\r\n' + \
                'Host: ' + host + '\r\n' + \
                'Connection: close\r\n\r\n'
            
            # send get command
            self.sendall(msg)

            #receive message and print it to stdout
            receivedMsg = self.recvall(self.socket)
            print(receivedMsg)

            #close connection and get return code and body.
            self.close()
            code = self.get_code(receivedMsg)
            body = self.get_body(receivedMsg)
            return HTTPResponse(code, body)


    # Post method handler
    def POST(self, url, args=None):
        port = 0
        host = ''
        path = ''
        query = ''
        fragment = ''
        length = 0
        body = ''

        # Parse url
        parsedUrl = urlparse(url)
        
        (host, port, path, query, fragment) = self.get_parsed_url(parsedUrl)

        # % encode all the necessary characters.
        if (args != None):
            for arg in args:
                body += arg.replace('%', '%25').replace('\n', '%0A') \
                    .replace('\r', '%0D').replace(' ', '%20').replace('"', '%22') \
                    .replace('\'', '%27') + '=' + args[arg].replace('%', '%25') \
                    .replace('\n', '%0A').replace('\r', '%0D').replace(' ', '%20') \
                    .replace('"', '%22').replace('\'', '%27') + '&'

            body = body[:-1]
            length = len(body)

        # check if the host and port are not empty
        if(port != 0 and host != ''):

            # connect to the server
            self.connect(host, port)

            # setup post request message
            msg = 'POST ' + path + query + fragment + ' HTTP/1.1\r\n' + \
                'Host: ' + host + '\r\n' + \
                'Content-Type: application/x-www-form-urlencoded\r\n' + \
                'Content-Length: ' + str(length) + '\r\n\r\n' + body

            # Send post request to server
            self.sendall(msg)

            # Receive message from server and print to stdout
            receivedMsg = self.recvall(self.socket)
            print(receivedMsg)

            # Close the connection and get return code and body
            self.close()
            code = self.get_code(receivedMsg)
            body = self.get_body(receivedMsg)
            return HTTPResponse(code, body)

    # Command used for calling get/post requsts
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
