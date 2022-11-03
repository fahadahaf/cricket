class Batting:
    def __init__(self):
        self.is_started = False
        self.at_end = None
        self.runs = 0
        self.num_balls = 0
        self.num_4s = 0
        self.num_6s = 0
        self.SR = 0
        self.num_dots = 0
        self.is_out = False
    
    def get_current_stats(self):
        return self.is_out
    
    def get_stats(self):
        return self.runs, self.num_balls, self.num_dots, self.num_4s, self.num_6s

    
    def update(self, result, *args):
        num_over = args[0]
        ball_num = args[1]
        if result.fair_delivery and result.extra['is_extra']==False:
            self.runs += result.score
        if result.fair_delivery and result.extra['wide']==False:
            self.num_balls += 1
        self.num_4s += 1 if result.boundary[4] else 0
        self.num_6s += 1 if result.boundary[6] else 0
        self.num_dots += 1 if result.score == 0 else 0
        if result.fair_delivery:
            self.is_out = True if result.wicket['is_out'] else False
        else:
            self.is_out = True if result.wicket['runout'] else False
        try:
            self.SR = round(100*(self.runs/self.num_balls), 0)
        except:
            self.SR = 0
        
