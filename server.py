#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip() # self.data is the encoded request header 

        decoded_data = self.data.decode().split("\r\n") # return original string of encoded data which is a byte array object
        
        # parsing for HTTP method and its path 
        http_method  = decoded_data[0].split(" ")[0] 
        path = decoded_data[0].split(" ")[1]
        # print(http_method, path)

        # when the method it not GET, return status code 405 
        # https://stackoverflow.com/a/8315292 - for sending response header 
        if http_method != "GET":
            self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n')
            self.request.sendall(b'Connection: close\r\n')

        # handling GET requests and path situations 
        elif http_method == "GET":
            # BUG w/ base.css ends in "/" fix
            # only happens on chrome, not firefox
            if ".css" in path and path.endswith("/"):
                path = path[:-1]

            # paths that end in "/" are to return "index.html" 
            if path.endswith('/'):
                path += "index.html"
            
            elif "/.." in path:
                self.request.sendall(b'HTTP/1.1 404 Not Found\r\n')
                self.request.sendall(b'Connection: close\r\n')
                return
            
            # try to open file; but if doesnt exist return 404
            try:
                # context-type (mime-type) needs to support files we serve     
                content_type = ''
                if "html" in path:
                    content_type = "text/html"
                elif "css" in path:
                    content_type = "text/css"

                # https://stackoverflow.com/a/55895307 - thread on serving files
                content_file = open("www" + path, "r")
                contents = content_file.read()
                content_file.close()

                self.request.sendall(b'HTTP/1.1 200 OK\r\n')
                self.request.sendall('Content-Type: {}\r\n'.format(content_type).encode())
                self.request.sendall(b'\r\n')
                self.request.sendall(contents.encode())
            
            # redirect on directory error (i.e. base_url + "/deep" test case)
            # specified this error based off inital exception returning [Errno 21]
            except IsADirectoryError:
                self.request.sendall(b'HTTP/1.1 301 Moved Permanently\r\n')
                self.request.sendall("Location: http://127.0.0.1:8080{}/\r\n".format(path).encode())

            except:
                self.request.sendall(b'HTTP/1.1 404 Not Found\r\n')
                self.request.sendall(b'Connection: close\r\n')


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
