import numpy as np
import time
from cricket.core.record import Record

class BasePlay:
    def __init__(self, pitch_type, is_powerplay, batsman, bowler):
        self.pitch_type = pitch_type
        self.is_powerplay = is_powerplay
        self.batsman = batsman
        self.bowler = bowler
        self.batting_offset = {'batsman':0.04, 'keeper':0.04, 'allrounder':0.01, 'bowler':-0.08}
        self.bowling_offset = {'allrounder':-0.02, 'bowler':0.02}
        self.outcome = ['fair', 'unfair']
        self.outcome_prob = [0.98, 0.02]
        self.fair = ['score','wicket']
        self.fair_prob = [0.9, 0.1]
        self.score = ['regular','extra']
        self.score_prob = [0.9, 0.1]
        self.extra = ['wide', 'bys']
        self.extra_prob = [0.6, 0.4]
        self.regular = ['runs', 'boundary']
        self.regular_prob = [0.85, 0.15]
        self.runs = [0,1,2,3,4,5,6]
        self.runs_prob = [0.5, 0.2, 0.18, 0.08, 0.02, 0.01, 0.01]
        self.boundary = [4,6]
        self.boundary_prob = [0.65, 0.35]
        self.wicket = ['bowled', 'caught', 'lbw', 'runout']
        self.wicket_prob = [0.2, 0.45, 0.25, 0.1]
    
    def update_prob_on_stats_and_info(self):
        bat_offset = self.batting_offset[self.batsman.style]
        bowl_offset = self.bowling_offset[self.bowler.style]

        bat_points = self.batsman.prime * 0.004 if self.batsman.style not in ['bowler'] else 0
        bowl_points = self.bowler.prime * 0.006

        if self.pitch_type == 'flat':
            bat_points += 0.1 * bat_points
            bowl_points -= 0.1 * bowl_points
        elif self.pitch_type == 'dusty':
            bat_points -= 0.05 * bat_points
            bowl_points += 0.1 * bowl_points if self.bowler.substyle == 'spinner' else 0
        else:
            bowl_points += 0.1 * bowl_points if self.bowler.substyle == 'pacer' else 0
        
        return bat_offset, bowl_offset, bat_points, bowl_points
        

    def update_probabilities(self):
        #if batsman.style in ['batsman', 'keeper', 'allrounder']:
        powerplay_offset = 0.1
        bat_offset, bowl_offset, bat_points, bowl_points = self.update_prob_on_stats_and_info()
        fair_prob = self.fair_prob[0] + (bat_offset*self.fair_prob[0]+bat_points) - (bowl_offset*self.fair_prob[0]+bowl_points)
        self.fair_prob = [fair_prob, 1-fair_prob]
        #print(self.fair_prob)
        if self.is_powerplay:
            regular_prob = self.regular_prob[1] + (bat_offset*self.regular_prob[1]+bat_points + powerplay_offset) - (bowl_offset*self.regular_prob[1]+bowl_points)
        else:
            regular_prob = self.regular_prob[1] + (bat_offset*self.regular_prob[1]+bat_points) - (bowl_offset*self.regular_prob[1]+bowl_points)
        self.regular_prob = [1-regular_prob, regular_prob]


def _score(batsman, bowler, pitch_type, is_powerplay):
    bp = BasePlay(pitch_type, is_powerplay, batsman, bowler)
    bp.update_probabilities()

    res1 = None
    res2 = None
    res3 = None
    res4 = None
    res0 = np.random.choice(bp.outcome, p=bp.outcome_prob)
    if res0 == 'fair':
        res1 = np.random.choice(bp.fair, p=bp.fair_prob)
        if res1 == 'score':
            res2 = np.random.choice(bp.score, p=bp.score_prob)
            if res2 == 'regular':
                res3 = np.random.choice(bp.regular, p=bp.regular_prob)
                if res3 == 'runs':
                    res4 = np.random.choice(bp.runs, p=bp.runs_prob)
                else:
                    res4 = np.random.choice(bp.boundary, p=bp.boundary_prob)
            else:
                res3 = np.random.choice(bp.extra, p=bp.extra_prob)
        else:
            res2 = np.random.choice(bp.wicket, p=bp.wicket_prob)

    return res0,res1,res2,res3,res4

def score(batsman, bowler, matchinfo):
    rc = Record()
    pitch_type, is_powerplay = matchinfo
    res0, res1, res2, res3, res4 = _score(batsman, bowler, pitch_type, is_powerplay)
    score = 0
    if res0 == 'unfair':
        rc.fair_delivery = False
        score = 1
    else:
        if res1 == 'wicket':
            rc.wicket['is_out'] = True
            rc.wicket[res2] = True
        else:
            if res2=='extra':
                rc.extra['is_extra'] = True
                rc.extra[res3] = True
                score = 1
            else:
                if res3 == 'boundary':
                    rc.boundary['is_boundary'] = True
                    rc.boundary[res4] = True
                else:
                    rc.run['is_run'] = True
                    rc.run['runs'] = res4
                score = res4
    rc.score = score
    return rc

def test(max_wickets=10, max_balls=120, sleep_time=0, verbose=False):
    wickets = 0
    runs = 0
    i = 0
    freehit = 0
    while i < max_balls:
        res0,res1,res2,res3,res4 = score()
        if res0 == 'unfair':
            freehit = 1
            continue
        if freehit:
            freehit = 0
            if res1=='wicket':
                if res2 == 'runout':
                    wickets += 1
            else:
                if res2 != 'regular':
                    runs += 1
                else:
                    runs += res4
        else:
            if res1=='wicket':
                wickets += 1
            else:
                if res2 != 'regular':
                    runs += 1
                else:
                    runs += res4
            i += 1
        if verbose:
            print(i, runs, wickets, res0, res1, res2, res3, res4)
        if wickets == max_wickets:
            break
        time.sleep(sleep_time)
    return wickets, runs

