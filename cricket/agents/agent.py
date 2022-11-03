from cricket.core.batting import Batting
from cricket.core.bowling import Bowling

class Human:
    def __init__(self,
                 first_name,
                 last_name,
                 country
                 ):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f'{first_name}, {last_name}'
        self.country = country
    
    def __str__(self):
        return self.first_name + ', ' + self.last_name + ', ' + self.country
    

class Player(Human):
    def __init__(self, 
                 id,
                 first_name, 
                 last_name, 
                 country, 
                 style='batsman',
                 substyle='-',
                 stats=None,
                 prime=0):
        super().__init__(first_name, last_name, country)
        self.id = id
        self.style = style
        self.substyle = substyle
        self.stats = stats
        self.prime = prime
        self.batting = Batting()
        self.bowling = Bowling()
    
    def set_stats(self, stats):
        self.stats = stats
    
    def get_stats(self):
        return self.stats
    
    def update_batting(self, result, *args):
        self.batting.update(result, *args)
    
    def update_bowling(self, result, *args):
        self.bowling.update(result, *args)

