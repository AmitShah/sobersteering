'''
Created on Aug 8, 2013

@author: amitshah
'''
import pymysql
from BlueRover import Api
import ssl,socket,sys
import os,tornado
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
import sys
from threading import Thread

class Observer(object):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, msg):
        for observer in self._observers:
            observer(message=msg)


class UpdateHandler(WebSocketHandler):
    observer = Observer()

    def open(self):
        UpdateHandler.observer.attach(self)
        #tornado.ioloop.IOLoop.instance().add_timeout(0.01,  self.loop)
        
    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        UpdateHandler.observer.detach(self)
        
    
    def __call__(self,message=None):
        self.on_message(message)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('home.html')
                
     
if __name__ == '__main__':
    
    api = Api(token='a8joj2YQbNagavsVVxy61NESKk+96IutuUKl7f/5',
              key='m0+svynws552oERs2nG4AmCYhbc1q0LGbsJI0VyRRHRPVLCk+y5F5B1rdAzh3lwY',
              base_url='https://developers.polairus.com')
    print api._key
    signature = api._generate_signature(api._key, "GET", "https://developers.polairus.com/eventstream")
    
    CRLF = '\r\n'
    request = [
               'GET /eventstream HTTP/1.1',
               'User-Agent: curl/7.21.3 (i686-pc-linux-gnu) libcurl/7.21.3 OpenSSL/0.9.8o zlib/1.2.3.4 libidn/1.18',
               'Host: developers.polairus.com',
               'Accept: */*',
               'Authorization:BR a8joj2YQbNagavsVVxy61NESKk+96IutuUKl7f/5:%s' %signature,
               '',
               '',
               ]
    
    def linesplit(socket):
        # untested
        buffer = socket.recv(4096)
        done = False
        while not done:
            if "\n" in buffer:
                (line, buffer) = buffer.split("\n", 1)
                yield line.strip() 
            else:
                more = socket.recv(4096)
                if not more:
                    done = True
                else:
                    buffer = buffer+more
        if buffer:
            yield buffer
            
    sock = socket.socket()    
    s = ssl.wrap_socket(sock)
    s.connect(('developers.polairus.com',443))    
    s.sendall(CRLF.join(request))
    generator = linesplit(s)            
    
    
    def process():
        data = generator.next()
        UpdateHandler.observer.notify(data)
    
    ioloop = tornado.ioloop.IOLoop.instance()
    pc = tornado.ioloop.PeriodicCallback(process,1000,io_loop=ioloop)
    
    
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret= 'secret_key',
        login_url='/login'
        )  
    application = tornado.web.Application([
    (r"/update", UpdateHandler),
    (r"/", MainHandler)       
    ], **settings)
    
    sockets = tornado.netutil.bind_sockets(9999)
    server = HTTPServer(application)
    server.add_sockets(sockets)
    
    pc.start()
    ioloop.start()
    
