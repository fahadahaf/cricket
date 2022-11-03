import numpy as np
from cricket.core.mechanics import score
from cricket.core.utils import *

class Match:
    def __init__(self, team1, team2, matchformat='T20', num_wickets=None, pitch_type = 'flat'):
        self.team1 = team1
        self.team2 = team2
        self.matchformat = matchformat
        self.format_dict = {'T10':10, 'T20':20, 'ODI':50}
        self.powerplay_dict = {'T10':3, 'T20':6, 'ODI':10}
        self.powerplay_length = self.powerplay_dict[self.matchformat]
        self.is_powerplay = None
        self.num_overs = self.format_dict[self.matchformat]
        self.pitch_type = pitch_type #green, dusty, flat
        self.num_wickets = len(team1.players)-1 if num_wickets is None else num_wickets
        self.choices = {'bat':True, 'field':False}
        self.toss_called = False
        self.toss_winner = None
        self.start_innings = False
        self.innings = 0
        self.match_winner = None
    
    def toss(self):
        winner = np.random.choice([self.team1.id, self.team2.id])
        if winner == self.team1.id:
            self.team1.batting_first = self.choices[self.team1.choose]
            self.team1.bowling_first = not(self.team1.batting_first)
            self.team2.batting_first = self.team1.bowling_first
            self.team2.bowling_first = not(self.team2.bowling_first)
        else:
            self.team2.batting_first = self.choices[self.team2.choose]
            self.team2.bowling_first = not(self.team2.batting_first)
            self.team1.batting_first = self.team2.bowling_first
            self.team1.bowling_first = not(self.team1.bowling_first)
        self.toss_called = True
        self.toss_winner = winner
        self.end_of_match = False
    
    def start(self):
        if self.end_of_match:
            print('End of match!')
            return
        if self.start_innings:
            print('Already started!')
            return
        self.is_freehit = False
        self.is_powerplay = True
        self.current_over = 0
        self.current_ball = 0
        if self.innings != 0:
            self.target_score = self.current_score + 1
            self.required_score = self.current_score + 1
            self.required_runrate = self.required_score/self.num_overs
        else:
            self.target_score = None
            self.required_score = None
            self.required_runrate = None
        self.current_score = 0
        self.current_runrate = 0
        self.current_wickets = 0
        self.num_fours = 0
        self.num_sixes = 0
        self.num_extras = 0
        self.num_wides = 0
        self.striker = 0
        self.nonstriker = 1
        self.bowler = 0
        if self.innings != 0:
            self.bowling_team = self.team1 if self.team1.batting_first else self.team2
            self.batting_team = self.team1 if self.team1.bowling_first else self.team2
            self.current_batsman = self.batting_team.players[self.batting_team.batting_order[self.striker]]
            self.current_bowler = self.bowling_team.players[self.bowling_team.bowling_order[self.bowler]]
        else:
            self.batting_team = self.team1 if self.team1.batting_first else self.team2
            self.bowling_team = self.team1 if self.team1.bowling_first else self.team2
            self.current_batsman = self.batting_team.players[self.batting_team.batting_order[self.striker]]
            self.current_bowler = self.bowling_team.players[self.bowling_team.bowling_order[self.bowler]]
        #if self.innings == 0:
        #    self.innings = 1
        #else:
        #    self.innings = 2
        self.start_innings = True
        self.end_innings = False

    def _swap_strikers(self):
        temp = self.striker
        self.striker = self.nonstriker
        self.nonstriker = temp
    
    def _update_strikers(self):
        temp = self.striker
        if self.striker < self.nonstriker:
            self.striker = self.nonstriker + 1
        else:
            self.striker = self.striker + 1
        if self.striker > self.num_wickets:
            self.striker = temp

    def update_batsmen(self, runs = False, over=False, wicket=False):
        if runs:
            self._swap_strikers()
        if over: #redundant, but might be useful later
            self._swap_strikers()
        if wicket:
            self._update_strikers()
        self.current_batsman = self.batting_team.players[self.batting_team.batting_order[self.striker]]
    
    def update_bowler(self, bowler_number=None):
        if bowler_number:
            self.bowler = bowler_number
        else:
            self.bowler = self.bowler + 1
        try:
            self.current_bowler = self.bowling_team.players[self.bowling_team.bowling_order[self.bowler]]
        except:
            self.bowler = 0
            self.current_bowler = self.bowling_team.players[self.bowling_team.bowling_order[self.bowler]]

    def update_record(self, result, is_freehit=False):
        self.current_batsman.update_batting(result, self.current_over, self.current_ball)
        self.current_bowler.update_bowling(result, self.current_over, self.current_ball)
        if self.is_freehit:
            if not result.fair_delivery:
                self.freehit = True
            else:
                self.is_freehit = False
                if not result.extra['wide']:
                    self.current_ball += 1
                if self.current_ball == 6:
                    self.current_ball = 0
                    self.current_over += 1
                if result.wicket['is_runout']:
                    self.current_wickets += 1
        else:
            if not result.fair_delivery:
                self.freehit = True
            else:
                self.is_freehit = False
                if not result.extra['wide']:
                    self.current_ball += 1
                if self.current_ball == 6:
                    self.update_batsmen(over=True)
                    self.update_bowler()
                    self.current_ball = 0
                    self.current_over += 1
                if result.wicket['is_out']:
                    self.current_wickets += 1
                    self.update_batsmen(wicket=True)
        if result.fair_delivery==False or result.extra['is_extra']==True:
            self.num_extras += 1
        self.num_fours += 1 if result.boundary[4] else 0
        self.num_sixes += 1 if result.boundary[6] else 0
        self.num_wides += 1 if result.extra['wide'] else 0
        if result.score in [1,3,5]:
            self.update_batsmen(runs=True)
        self.current_score += result.score
        try:
            self.current_runrate = calculate_runrate(self.current_score, self.current_over, self.current_ball)
        except:
            self.current_runrate = 0
        if self.current_over >= self.powerplay_length:
            self.is_powerplay = False
        if self.required_score is not None: #or self.innings > 0
            self.required_score -= result.score
            self.required_runrate = calculate_runrate(self.required_score, self.current_over, self.current_ball,
                                                      required=True, num_overs=self.num_overs)
            if self.current_score > self.target_score:
                self.end_innings = True
                self.innings += 1
                self.match_winner = self.batting_team
                return
        if self.current_wickets == self.num_wickets or self.current_over==self.num_overs:
            if self.innings > 0:
                if self.current_score < self.target_score-1:
                    self.match_winner = self.bowling_team
                elif self.current_score == self.target_score-1:
                    self.match_winner = None
                else:
                    self.match_winner = self.batting_team
            self.end_innings = True
            self.innings += 1   

    def update_from_scorecard(self, scorecard):
        #TO-DO
        return

    def next(self, next_batsman=None, next_bowler=None):
        '''
        Next delivery.
        '''
        if self.end_of_match:
            print('End of match!')
            return
        if not self.start_innings:
            print('innings not started!') #should raise some error
            return
        if self.end_innings:
            if self.innings > 1:
                match_result = 'Drawn' if self.match_winner is None else self.match_winner.name
                print(f'End of match! Winner: {match_result}')
                self.end_of_match = True
            else:
                print('First innings done! please start the second innings.')
            self.start_innings = False
            return
        match_info = [self.pitch_type, self.is_powerplay]
        result = score(self.current_batsman, self.current_bowler, match_info) #stats and other params will be passed to it later
        #print(f'Batsman: {self.current_batsman.full_name}, Bowler: {self.current_bowler.full_name}')
        #print(self.current_batsman.batting.get_stats())
        self.update_record(result)
        #print(result.score, self.current_score, self.current_wickets, 
        #      f"{self.current_over}.{self.current_ball}",
        #      self.num_fours, self.num_sixes, self.num_wides, self.num_extras,
        #      self.current_runrate, self.required_score, self.required_runrate)

# import time
# from cricket.play.match import Match
# from cricket.agents.team import Team
# tm1 = Team('pk92', 'Pakistan')
# tm2 = Team('in91', 'India')
# tm1.add_players_from_file('datasets/teams/pakistan.csv')
# tm2.add_players_from_file('datasets/teams/india.csv')
# match = Match(tm1, tm2)
# match.toss()
# match.start()
# print(match.batting_team.name)
# while (True):
#     match.next()
#     time.sleep(0.5)
#     if match.end_innings:
#         break
# match.next()
# match.start()
# while (True):
#     match.next()
#     time.sleep(0.5)
#     if match.end_innings:
#         break
# match.next()

        
        

        