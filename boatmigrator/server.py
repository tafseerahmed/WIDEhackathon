#!/usr/bin/env python

import json 
from http.server import BaseHTTPRequestHandler, HTTPServer

from places import Places
from search import paged_search, vectorized

places = Places('yso-paikat-skos.rdf')

class RequestHandler(BaseHTTPRequestHandler): 
    def do_GET(self):
        if 'api' in self.path:
            subject = self.path.strip().split('/')[2]
            results = paged_search(subject, places)
            vector = vectorized(results, places)

            #geojson = {"type": "Feature", "geometry": { "type": "Polygon", "coordinates": vector}}

            self.send_response(200)

            self.send_header('Content-type','text/json')
            self.end_headers()

            self.wfile.write(bytes(json.dumps(vector), "utf8"))
        elif 'geojson' in self.path:
            self.send_response(200)

            self.send_header('Content-type','text/json')
            self.end_headers()
            
            geo = ''
            with open('finland.geojson', 'r') as f:
                geo = bytes(f.read(), 'utf8')

            self.wfile.write(geo)
        else:
            self.send_response(200)

            self.send_header('Content-type','text/html')
            self.end_headers()

            index = ''
            with open('index.html', 'r') as f:
                index = bytes(f.read(), 'utf8')

            self.wfile.write(index)

print('starting server...')
httpd = HTTPServer(('127.0.0.1', 8000), RequestHandler)
httpd.serve_forever()