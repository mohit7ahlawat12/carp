from google.appengine.ext import db 

class users(db.Model):
    ukey = db.StringProperty()
    email = db.EmailProperty()

class UserManager():
    def Add(self,email):
        #email = email.replace('%40','@')
        if not self.__checkEmailExists(email):
            user = users()
            user.email = db.Email(email)
            user.put()
            user.ukey = str(user.key())
            user.put()
            return str(user.key())
        else:
            return str(False)
    
    def __checkEmailExists(self,email):
        query = db.Query(users)
        query = users.all()
        query.filter('email =',email)
        
        if(query.count(1) == 1):
            #email exists
            return True
        else:
            return False 