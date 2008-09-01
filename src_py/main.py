import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db 

def toNum(s):
    """Convert string to either int or float."""
    try:
        ret = int(s)
    except ValueError:
        #Try float.
        ret = float(s)
    return ret

class users(db.Model):
    ukey = db.StringProperty()
    email = db.EmailProperty()

class journeys(db.Model):
    jkey = db.StringProperty()
    start = db.GeoPtProperty()
    end = db.GeoPtProperty()
    user = db.ReferenceProperty(users, collection_name='user_journeys')
    
class AddUser(webapp.RequestHandler):
    def post(self):
        user = users()
        user.email = db.Email(self.request.get('email'))
        user.put()
        user.ukey = str(user.key())
        user.put()
        self.redirect('/display')

class AddJourney(webapp.RequestHandler):
    def post(self):
        journey = journeys()
        journey.start = db.GeoPt(self.request.get('slat'),self.request.get('slon')  )
        ukey = self.request.get('ukey')
        journey.user = users.get(db.Key(ukey))
        journey.put()
        journey.jkey = str(journey.key())
        journey.put()
        self.redirect('/display')
        
class Display(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""<html><body>""")
        q = db.GqlQuery("SELECT * FROM users")
        results = q.fetch(20)
        for u in results:
            self.response.out.write("<div>email %s /n ukey %s</div>" % (u.email,u.ukey))
        
        self.response.out.write("""<div>==================</div>""")
        
        q = db.GqlQuery("SELECT * FROM journeys")
        results = q.fetch(20)
        for j in results:
            self.response.out.write("<div>slat: %s slon: %s jkey: %s</div>" % (j.start.lat, j.start.lon, j.jkey))
        self.response.out.write("""<body><html>""")
        
class AddData(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<html><body>
          
          <form action="/addu" method="post">
            <div>email<input name="email"></input></div>
            <div><input type="submit" value="register"></div>
          </form>
          
          <form action="/addj" method="post">
            <div>slat<input name="slat"></input></div>
            <div>slon<input name="slon"></input></div>
            <div>uid<input name="ukey" value ="3"></input></div>
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
    


class Add(webapp.RequestHandler):
    def post(self):
        a = toNum(self.request.get('a'))
        b = toNum(self.request.get('b'))
        answer = a+b
        self.response.out.write(answer)
    def get(self):
        a = toNum(self.request.get('a'))
        b = toNum(self.request.get('b'))
        answer = a+b
        self.response.out.write(answer)
        
class Dummy(object):
    __name__ = 'Dummy'
    def __init__(self):
        self.d1 = 'a'
        self.d2 = 'b'
        self.d3 = 'c'

class JSON(webapp.RequestHandler):
  def get(self):
    #self.response.out.write('<html><body>')
    #self.response.out.write(json.write(Dummy()))
    #self.response.out.write("""</body></html>""")
    self.response.out.write('{"validated":"This request was spoofed","query":[],"url":"http:\/\/graargh.returnstrue.com\/buh\/fetchme.php","signature":"","signature_len":1}')
    self.response.headers.add_header("Content-Type", "text/javascript")

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/addd',AddData),
                                      ('/addu',AddUser),
                                      ('/addj',AddJourney),
                                      ('/display',Display),
                                      ('/json',JSON),
                                      ('/add', Add)],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()