'''
Created on Aug 8, 2013

@author: amitshah
'''
import idatabase as database
from bluerover import Api
import ssl,socket,sys
import os,tornado
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
import sys,functools,json

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

class BaseHandler(tornado.web.RequestHandler):
        
    def initialize(self,event_service,account_service,configuration_service):
        self.event_service = event_service
        self.account_service = account_service
        self.configuration_service = configuration_service
        pass
    
    def get_current_user(self):
        '''used for web api administration access'''
        #self.account_service.getUserWithPassword()
        user = self.get_secure_cookie('user')
        if user is not None:            
            user = json.loads(self.get_secure_cookie("user"))
        return user

class LoginHandler(BaseHandler):
    
    def get(self):
        self.render('login.html')
    def post(self):
        userid = self.get_argument('userid', True)
        password = self.get_argument('password',True)
        user = self.account_service.getUserWithPassword(userid,password)
        if user is not None:            
            self.set_secure_cookie("user",json.dumps(user.to_dict()))
            self.redirect(self.get_argument("next", u"/"))
        else:
            self.render('login.html',message='Error logging in, please try again.\
            If you continue to experience issues, please contact support')

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")
        
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
    
    
    sock = socket.socket()    
    s = ssl.wrap_socket(sock)
        
    def connect_to_service():        
        s.connect(('developers.polairus.com',443))    
        s.sendall(CRLF.join(request))
    
    def data_handler(sock,fd,events):
        try:
            data = sock.recv(4096)
            UpdateHandler.observer.notify(data)        
        except:
            sock.close()
            tornado.ioloop.IOLoop.instance().add_callback(connect_to_service)            
        pass

    callback = functools.partial(data_handler, s)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(s.fileno(), callback, ioloop.READ)
    
    ioloop.add_callback(connect_to_service)
    #pc = tornado.ioloop.PeriodicCallback(periodic_func,10,io_loop=ioloop)
    
    #define all the services
    services = dict(
        event_service = database.StateService(database.CONNECTION_STRING),\
        configuration_service = database.ConfigurationService(database.CONNECTION_STRING),\
        account_service = database.AccountService(database.CONNECTION_STRING)
        )
    
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
    
    #pc.start()
    ioloop.start()
    
