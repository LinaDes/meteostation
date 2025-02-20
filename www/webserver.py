#!/usr/bin/python
# - *- coding: utf- 8 - *-

import http.server
import cgitb
cgitb.enable()

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler
server_address = ("", 8000)
handler.cgi_directories = ["/cgi-bin"]

httpd = server(server_address, handler)
httpd.serve_forever()
