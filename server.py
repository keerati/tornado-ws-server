import tornado
import json

from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

define("port", default=8888, help="run on the given port", type=int)

clients = []

class IndexHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html", port=options.port)

class PostMsgHandler(RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        try:
            data = json.loads(self.request.body)
        except:
            data = {}
        msg = data.get("msg","default msg")
        print clients
        for client_socket in clients:
            print 'Push message to client %s' % repr(client_socket)
            client_socket.write_message(msg)

        self.set_status(201)
        self.finish()

class WebSocketHandler(WebSocketHandler):
    def open(self, *args):
        self.stream.set_nodelay(True)
        clients.append(self)
        print "after create a new socket", clients

    def on_message(self, message):        
        print "Received a message : %s" % message
        
    def on_close(self):
        clients.remove(self)

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/post', PostMsgHandler),
    (r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
