class JourneyResult:
    #@param journey: a journey being compared
    #@param total_disp: Total displacement of this journey from the reference journey 
    def __init__(self,t):
        self.total_disp = t

class JourneyResults:
    def __init__(self,capacity):
        #maximum number of journeys
        self.capacity = capacity
        #container of resulting journeys
        self.journey_list = []
        #maximum acceptable displacement between points
        self.max_disp = None
        
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
    #ordered list from min to max displacement
    def __orderedInsert(self,journey_result):

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

jr = JourneyResults(6)
jr.insert(JourneyResult(4))
jr.insert(JourneyResult(23))
jr.insert(JourneyResult(4))
jr.insert(JourneyResult(2))
jr.insert(JourneyResult(1))
jr.insert(JourneyResult(11))
jr.insert(JourneyResult(7))
jr.insert(JourneyResult(8))
for j in jr.journey_list:
    print j.total_disp