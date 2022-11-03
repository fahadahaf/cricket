def bowled_balls(overs, balls):
    return (overs*6) + balls

def remaining_balls(overs, balls, num_overs):
    balls_bowled = bowled_balls(overs, balls)
    return (num_overs * 6) - balls_bowled

def calculate_runrate(score, overs, balls, required=False, num_overs=None):
    if required:
        return (6*score) / remaining_balls(overs, balls, num_overs)
    else:
        return (6*score) / bowled_balls(overs, balls)

def calculate_bowler_economy(runs, overs, balls):
    denom = overs + (balls/6)
    try:
        return round(runs/denom, 2)
    except:
        return 0