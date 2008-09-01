from google.appengine.ext import db
from math import acos,sin,cos,radians
import users


class journeys(db.Model):
    jkey = db.StringProperty()
    desc = db.StringProperty()
    start = db.GeoPtProperty()
    end = db.GeoPtProperty()
    user = db.ReferenceProperty(users.users, collection_name='user_journeys')
    
class JourneyManager():
    
    def AddJourney(self,desc,ukey,slat,slon,elat,elon):
        journey = journeys()
        journey.start = db.GeoPt(slat,slon)
        journey.end = db.GeoPt(elat,elon)
        journey.desc = desc
        journey.user = users.users().get(db.Key(ukey))
        journey.put()
        journey.jkey = str(journey.key())
        journey.put()
        return str(journey.key())
    
    def GetSimilarJourneys(self,jkey):
        refj = journeys.get(db.Key(jkey))
        q = db.Query()
        
        orig_lat = refj.start.lat
        orig_lon = refj.start.lon
        
        dest_lat = refj.end.lat
        dest_lon = refj.end.lon
        
        q = journeys.all()
        for j in q:
            distance = distancePts(orig_lat,orig_lon,j.start.lat,j.start.lon,'km')
        
    def distancePts(self,lat1,lon1,lat2,lon2,units):
        if units == 'km':
            factor = 6371.0
        elif units == 'miles':
            factor = 3959.0
        return (factor*acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians( lat2))))

class RefMarker:
    def __init__(self,jour,disp, start):
        self.jour = jour
        self.disp = disp
        self.start = start

#Container of journeys, limited in size. Where limit is reached, largest item is removed. Inserts in order or increasing distance 
#if disp <= range: jl.insert(JourDisp(j,disp))
class JourneyList:
    def __init__(self,capacity):
        self.capacity = capacity
        self.journeys = []
        self.max_disp = None
        
    def insert(self,ref_marker):
        if self.max_disp == None:
            #First item in list
            journeys.append(ref_marker)
            max_disp = ref_marker.disp
            return True
        else:
            if (ref_marker.disp > max_disp) and (self.journeys.len() < self.limit):
                #new max distance item, but no need to pop largest from list
               self.__orderedInsert(ref_marker)
               
            elif (distance < max_dist) and (self.journeys.len() >= self.limit):
                #capacity reached, pop largest item off
                self.__orderedInsert(jour_disp)
                journeys.pop()

    #max: append, otherwise insert
    def __orderedInsert(self,jour_disp):
        pos = 0
        for jd in journeys:
            if jour_disp.disp > jd.disp:
                journeys.insert(x,jour_disp)
                break
            pos += 1