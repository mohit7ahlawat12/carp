import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db 
from django.utils import simplejson
import urllib
from urlparse import urlparse

import journeys
import users
 
def toNum(s):
    """Convert string to either int or float."""
    try:
        ret = int(s)
    except ValueError:
        #Try float.
        ret = float(s)
    return ret
       
class Display(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""<html><body>""")
        
        q = db.GqlQuery("SELECT * FROM users")
        for u in q:
            self.response.out.write("""<div>==========User==========</div>""")
            self.response.out.write("<div>email %s | ukey %s</div>" % (u.email,u.ukey))
            for j in u.user_journeys:
                self.response.out.write("<div>====Journey: desc: %s | s: %s,%s | e: %s,%s | jkey: %s | ukey: %s</div>" % (j.desc, j.start.lat, j.start.lon, j.end.lat, j.end.lon, j.jkey, str(j.user.ukey)))
        self.response.out.write("""<body><html>""")
        
class AddData(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<html><body>
          
          <form action="/rpc" method="get">
            <div>function<input name="action" value="AddUser"></input></div>
            <div>email<input name="email"></input></div>
            <div><input type="submit" value="register"></div>
          </form>
          
          <form action="/rpc" method="get">
            <div>function<input name="action" value="AddJourney"></input></div>
            <div>desc<input name="desc" value="Home to Wits"></input></div>
            <div>slat<input name="slat" value="-26.066763"></input></div>
            <div>slon<input name="slon" value="28.051003"></input></div>
            <div>elat<input name="elat" value="-26.18858"></input></div>
            <div>elon<input name="elon" value="28.030286"></input></div>
            <div>uid<input name="ukey" value ="agRjYXJwcgsLEgV1c2VycxgHDA"></input></div>
            <div><input type="submit" value="addj"></div>
          </form>
        </body>
      </html>""")
    
class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<html><body>
          <form action="/addj" method="post">
            <div><input name="a"></textarea></div>
            <div><input name="b"></textarea></div>
            <div><input type="submit" value="Add"></div>
          </form>
        </body>
      </html>""")

class JSON(webapp.RequestHandler):
  def get(self):
    #self.response.out.write('<html><body>')
    #self.response.out.write(json.write(Dummy()))
    #self.response.out.write("""</body></html>""")
    self.response.out.write('{"validated":"This request was spoofed","query":[],"url":"http:\/\/graargh.returnstrue.com\/buh\/fetchme.php","signature":"","signature_len":1}')
    self.response.headers.add_header("Content-Type", "text/javascript")

class RPCHandler(webapp.RequestHandler):
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.methods = RPCMethods()
    
    def get(self):
        func = None
        
        url = urlparse(urllib.unquote_plus(self.request.url))
        #Split parameters into a dictionary lookup: http://atomized.org/2008/06/parsing-url-query-parameters-in-python/
        params = dict([part.split('=') for part in url[4].split('&')])
        
        action = params['action']
        if action:
          if action[0] == '_':
            #Attempt to access restricted function
            self.error(403) # access denied
            return
          else:
            #idnetify function based on passed action
            func = getattr(self.methods, action, None)
       
        if not func:
            #Invalid action supplied
          self.error(404) # file not found
          return

        #Call action and pass parameters 
        result = func(params)
        self.response.out.write(result)
        
class RPCMethods:
  """ Defines the public methods that can be called over HTTP
  NOTE: Do not allow remote callers access to private/protected "_*" methods.
  """
  def __init__(self):
    self.user_manager = users.UserManager()
    self.journey_manager = journeys.JourneyManager()

  def AddJourney(self,param):
      return self.journey_manager.AddJourney(param['desc'],param['ukey'], param['slat'], param['slon'], param['elat'], param['elon'])
  def AddUser(self,param):
      return self.user_manager.Add(param['email'])
  
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/addd',AddData),
                                      ('/display',Display),
                                      ('/rpc',RPCHandler),
                                      ('/json',JSON)],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()