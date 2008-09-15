from google.appengine.ext import db
from math import acos,sin,cos,radians
from decimal import * 

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
    
    #@param jkey: string key of reference journey to find matches
    #@param num: number of journeys to return
    #@param units: units "km" or "miles"
    #@param threshold: maximum distance between either origin or destination
    def GetSimilarJourneys(self,jkey,num,units,threshold):
        
        #list of resulting journeys
        results = JourneyList(num)
        
        refj = journeys.get(db.Key(jkey))
        #q = db.Query()
        
        #get co-ordinates of reference journey
        orig_lat = refj.start.lat
        orig_lon = refj.start.lon
        dest_lat = refj.end.lat
        dest_lon = refj.end.lon
        
        q = journeys.all()
        for j in q:
            #TODO: perform rough estimate first (improve performance)
            #perform more accurate calculation
            start_disp = distancePts(orig_lat,orig_lon,j.start.lat,j.start.lon,units)
            end_disp = distancePts(dest_lat,dest_lon,j.end.lat,j.end.lon,units)
            total_distance = start_distance + end_distance
            
            jour_disp = JourneyDisp(j,start_disp,end_disp)
            
            if(jour_disp.total_disp < threshold):
                #Update reference list
                results.insert(jour_disp)
        
        return results
    
    def distancePts(self,lat1,lon1,lat2,lon2,units):
        if units == 'km':
            factor = 6371.0
        elif units == 'miles':
            factor = 3959.0
            #The Haversine formula
            #http://www.movable-type.co.uk/scripts/latlong.html
            #http://code.google.com/apis/maps/articles/phpsqlsearch.html#findnearsql
        
        distance = (factor*acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians( lat2))))

        #set precision
        getcontext().prec = 4
        return Decimal(str(distance))
     
#Simple container object to store a journey reference and the total displacement for distance comparison
class JourneyDisp:
    #@param journey: a journey being compared
    #@param total_disp: Total displacement of this journey from the reference journey 
    def __init__(self,journey,start_disp,end_disp):
        self.journey = journey
        self.start_disp = start_disp
        self.end_disp = end_disp
        self.total_disp = start_disp + end_disp
        
#Container of journeys, limited in size. Where limit is reached, largest item is removed. Inserts in order or increasing distance 
#if disp <= range: jl.insert(JourDisp(j,disp))
#Class ensures that the top journeys are returned in order
class JourneyList:
    def __init__(self,capacity):
        #maximum number of journeys
        self.capacity = capacity
        #container of resulting journeys
        self.journey_list = []
        #maximum acceptable displacement between points
        self._max_disp = None
        
    def insert(self,jour_disp):
        if self._max_disp == None:
            #First item in list
            self.journeys.append(jour_disp)
            #update the maximum displacement
            self.max_disp = jour_disp.total_disp
            return True
        else:
            if (self.journeys.len() < self.capacity):
                #new max distance item, but no need to pop largest from list
               self.__orderedInsert(jour_disp)
            elif (jour_disp.total_disp < max_dist) and (self.journeys.len() >= self.capacity):
                #shorter journey, capacity reached, pop largest item off
                self.__orderedInsert(jour_disp)
                journeys.pop()

    #max: append, otherwise insert
    def __orderedInsert(self,jour_disp):
        pos = 0
        for jd in self.journey_list:
            if jour_disp.total_disp > jd.total_disp:
                journeys.insert(pos,jour_disp)
                break
            pos += 1
            
        if(self.max_disp < jour_disp.total_disp):
            #update the maximum displacement
            self.max_disp = jour_disp.total_disp
            