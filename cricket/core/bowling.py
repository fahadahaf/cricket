from cricket.core.utils import calculate_bowler_economy
class Bowling:
    def __init__(self):
        self.is_started = False
        self.runs = 0
        self.num_4s = 0
        self.num_6s = 0
        self.wickets = 0
        self.num_overs = 0
        self.ball_num = 0 # from 1 to 6
        self.num_wides = 0
        self.num_noballs = 0
        self.num_maiden_overs = 0
        self.num_dots = 0
        self.prev_runs = 0
        self.prev_over = 0
        self.econ = 0
    
    def get_current_stats(self):
        return self.num_overs
    
    def get_stats(self):
        return self.wickets, self.runs, self.num_dots, self.num_4s, self.num_6s, self.num_maiden_overs, f'{self.num_overs}.{self.ball_num}'
    
    def update(self, result, *args):
        if not result.extra['bys']:
            self.runs += result.score
        self.num_4s += 1 if result.boundary[4] else 0
        self.num_6s += 1 if result.boundary[6] else 0
        self.num_dots += 1 if result.score == 0 else 0
        if result.fair_delivery:
            self.wickets += 1 if result.wicket['is_out'] else 0
        if result.fair_delivery and result.extra['wide']==False:
            self.ball_num += 1
            self.num_overs += 1 if self.ball_num==6 else 0
            self.ball_num %= 6
        self.num_wides += 1 if result.extra['wide'] else 0
        self.num_noballs += 0 if result.fair_delivery else 1
        if self.prev_over < self.num_overs:
            self.prev_over = self.num_overs
            if self.prev_runs == self.runs:
                self.num_maiden_overs += 1
            self.prev_runs = self.runs
        self.econ = calculate_bowler_economy(self.runs, self.num_overs, self.ball_num)

        
