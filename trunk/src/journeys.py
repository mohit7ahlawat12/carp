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
        
        #empty list of resulting journeys
        results = JourneyResults(num)
        
        refj = journeys.get(db.Key(jkey))
        if(refj != None):
            #q = db.Query()
            
            #get co-ordinates of reference journey
            orig_lat = refj.start.lat
            orig_lon = refj.start.lon
            dest_lat = refj.end.lat
            dest_lon = refj.end.lon
            
#            q = journeys.gql("""WHERE jkey != :jk""" 
#                      "AND ANCESTOR IS :u"""
#                      ,jk=jkey, u = refj.user)
            
            #iterate over journeys
            q = journeys.all()
            for j in q:
                #don't check reference journey or users journeys
                if((refj.user.ukey != j.user.ukey) and (refj.jkey != j.jkey)):
                    #TODO: perform rough estimate first (improve performance)
                    #perform more accurate calculation
                    start_disp = self.distancePts(orig_lat,orig_lon,j.start.lat,j.start.lon,units)
                    end_disp = self.distancePts(dest_lat,dest_lon,j.end.lat,j.end.lon,units)
                    total_disp = start_disp + end_disp
                    precision = 4
                    result = JourneyResult(j,start_disp,end_disp,precision)
                
                    if(result.total_disp < threshold):
                        #Update results list
                        results.insert(result)
        
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


        return Decimal(str(distance))
     
#Simple container object to store a journey reference and the total displacement for distance comparison
class JourneyResult:
    #@param journey: a journey being compared
    #@param total_disp: Total displacement of this journey from the reference journey 
    def __init__(self,journey,start_disp,end_disp,precision):
        #set precision
        getcontext().prec = precision
        self.journey = journey
        self.start_disp = start_disp * 1
        self.end_disp = end_disp * 1
        self.total_disp = start_disp + end_disp
        
#Container of journeys, limited in size. Where limit is reached, largest item is removed. Inserts in order or increasing distance 
#Class ensures that the shortest journeys are returned in order
class JourneyResults:
    def __init__(self,capacity):
        #maximum number of journeys
        self.capacity = capacity
        #container of resulting journeys
        self.journey_list = []
        #longest displacement of journey in journey list
        self.max_disp = None
    
    #Insert a journey result into this container. If capacity is reached then largest item is removed.
    #Items inserted into journey_list in order
    def insert(self,jour_result):
        if (self.max_disp == None):
            #First item in list
            self.journey_list.append(jour_result)
            #update the maximum displacement
            self.max_disp = jour_result.total_disp
            return True
        else:
            if (len(self.journey_list) < self.capacity):
                #new max distance item, but no need to pop largest from list
               self.__orderedInsert(jour_result)
            elif (jour_result.total_disp < self.max_disp) and (len(self.journey_list) >= self.capacity):
                #shorter journey, capacity reached, pop largest item off
                self.__orderedInsert(jour_result)
                self.journey_list.pop()

    #max: append, otherwise insert
    #TODO: check
    #ordered insert to list from min to max displacement
    def __orderedInsert(self,journey_result):
        if (len(self.journey_list) < self.capacity):    
            #simple if item 
            if(journey_result.total_disp >= self.max_disp):
                #update the maximum displacement, append to end of list
                self.max_disp = journey_result.total_disp
                self.journey_list.append(journey_result)
            else:    
                        
                #insert in ordered position
                #if smaller than current, insert in previous position
                pos = 0
                for jr in self.journey_list:
                    #if < current, place before else check next
                    if (journey_result.total_disp <= jr.total_disp):
                        self.journey_list.insert(pos,journey_result)
                        break
                    pos += 1