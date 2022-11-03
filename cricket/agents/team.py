import pandas as pd
from cricket.agents.agent import Player

class Team:
    def __init__(self, id, name, choose='bat', num_players=11, num_bowlers=5):
        self.id = id
        self.name = name
        self.players = []
        self.choose = choose
        self.batting_first = True
        self.bowling_first = False
        self.num_players = num_players
        self.num_bowlers = num_bowlers
        self.batting_order = [i for i in range(0, num_players)]
        self.bowling_order = [i for i in range(num_players-num_bowlers, num_players)]
    
    def add_players(self, players):
        self.players += players

    def add_player(self, player):
        self.players.append(player)

    def add_players_from_file(self, filename, update_id=True):
        df = pd.read_csv(filename, sep=',')
        if df['prime'].max() > 5:
            raise ValueError('A player cannot have more than 5 prime points!')
        if df['prime'].sum() > 11:
            raise ValueError('Maximum allowed prime points per team are 11!')
        if update_id:
            self.id = df['team_id'][0]
        for i in range(0, df.shape[0]):
            pl = Player(df['player_id'][i],
                        df['first_name'][i],
                        df['last_name'][i],
                        df['country'][i],
                        df['style'][i],
                        df['substyle'][i],
                        df['stats'][i],
                        df['prime'][i])
            self.add_player(pl)
    
    def set_batting_order(self, order_list=[]):
        if len(self.players) < self.num_players:
            raise ValueError('Team incomplete! please add players.')
        if len(order_list) == 0:
            order_list = [i for i in range(0, self.num_players)] 
        elif len(order_list) != self.num_players:
            raise ValueError('Provided order should match the number of players.')
        self.batting_order = order_list
    
    def set_bowling_order(self, order_list=[]):
        count_bowlers = 0
        if len(order_list)!=0:
            self.bowling_order = order_list
        else:
            count_bowlers=0
            counter = 0
            for pl in self.players:
                if pl.style in ['bowler', 'allrounder']:
                    order_list.append(counter)
                    count_bowlers += 1
                counter += 1
                if len(order_list) == self.num_bowlers:
                    break
            if count_bowlers < self.num_bowlers:
                raise ValueError('Not enough bowlers in the team! please add bowling players.')
            self.bowling_order = order_list
