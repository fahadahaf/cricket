class Scorecard:
    def __init__(self):
        return

class Record:
    def __init__(self):
        self.wicket = {'is_out':False, 
                    'lbw':False, 
                    'bowled':False,
                    'caught':False,
                    'runout':False}
        self.extra = {'is_extra':False, 
                      'wide':False,
                      'bys':False}
        self.boundary = {'is_boundary':False, 
                         4:False, 
                         6:False}
        self.run = {'is_run':False, 
                    'runs':0}
        self.score = 0
        self.fair_delivery = True




