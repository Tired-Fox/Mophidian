import http.server
import socketserver

PORT = 3000
class HttpRequestHandler (http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.path = 'playground/web/index.html'
		return http.server.SimpleHTTPRequestHandler.do_GET(self)
		
Handler = HttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
	print("Http Server Serving at port", PORT)
	httpd.serve_forever()
    httpd.
