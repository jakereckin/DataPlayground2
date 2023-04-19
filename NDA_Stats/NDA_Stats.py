import pandas as pd

class read_data:

    def __init__(self, file) -> None:
        self.file = file 

    def read_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.file)

class get_stats:

    def __init__(self, game, players, stats) -> None:
        self.game = game 
        self.players = players 
        self.stats = stats 
        self.game_stats : pd.DataFrame
        self.full_stats : pd.DataFrame

    def merge_data(self) -> 'get_stats':
        stats_summed = self.stats.groupby(by = ['Game_ID'], as_index = False)[['2FGM', '2FGA', '3FGM', '3FGA', 'FTM', 'FTA', 'Off_Reb', 'Def_Reb', 'Assist', 'Steal', 'Block', 'Turnover']].sum()
        self.game_stats = pd.merge(stats_summed, self.game, on = 'Game_ID')
        self.full_stats = pd.merge(self.stats, self.players, on = 'Player_ID').merge(self.game, on = 'Game_ID')
        return self

    def format_stats(self) -> 'get_stats':
        self.full_stats['FGA'] = self.full_stats['2FGA'] + self.full_stats['3FGA']
        self.full_stats['FGM'] = self.full_stats['2FGM'] + self.full_stats['3FGM']
        self.full_stats['Points'] = (2 * self.full_stats['2FGM']) + (3 * self.full_stats['3FGM']) + self.full_stats['FTM']
        self.game_stats['FGA'] = self.game_stats['2FGA'] + self.game_stats['3FGA']
        self.game_stats['FGM'] = self.game_stats['2FGM'] + self.game_stats['3FGM']
        self.game_stats['Points'] = (2 * self.game_stats['2FGM']) + (3 * self.game_stats['3FGM']) + self.game_stats['FTM']
        return self