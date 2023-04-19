from dataclasses import field
import pickle
from flask import Flask, request, jsonify, render_template
import pandas as pd 
import random 
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class load_modules:

    def __init__(self, file):
        self.file = file 


    def load_file(self):
        file = pickle.load(open(self.file, 'rb'))
        return file 

class advanced_stats:

    def __init__(self, fgm, fga, ftm, fta, threepm, threepa, or_o, dr, a, to, st):
        self.fgm = fgm 
        self.fga = fga 
        self.ftm = ftm 
        self.fta = fta 
        self.threepm = threepm 
        self.threepa = threepa 
        self.or_o = or_o
        self.dr = dr 
        self.a = a
        self.to = to 


    def offensive_efficiency(self):
        if (self.fga + self.a + self.to - self.or_o) > 0:
            return ((self.ftm + self.a) / (self.fga + self.a + self.to - self.or_o))
        else:
            return 0

    def get_ppa_two(self):
        total_points = 2 * (self.fgm - self.threepm)
        total_attempts = (self.fga - self.threepa)
        if total_attempts > 0:
            return total_points / total_attempts
        else:
            return 0

    def get_ppa_three(self):
        total_points = 3 * self.threepm
        total_attempts = self.threepa
        if total_attempts > 0:
            return total_points / total_attempts
        else:
            return 0

    def get_total_ppa(self):
        total_points = 2 * (self.fgm - self.threepm) + 3 * self.threepm
        total_attempts = self.fga
        if total_attempts > 0:
            return total_points / total_attempts
        else:
            return 0

    def team_scoring_poss(self):
        team_attempts = self.fgm
        if self.fta > 0:
            inner_part = (1 - (1 - (self.ftm / self.fta) ** 2))
        else:
            inner_part = 0
        return team_attempts + inner_part *  self.fta * 0.4

    def team_play_percent(self, sp):
        numerator = sp
        denom = self.fga + self.fta * 0.4 + self.to
        if denom > 0:
            return numerator / denom
        else:
            return 0

    def possesions(self):
        other_team_def_rebounds = (self.fga - self.fgm) - self.or_o
        if (self.or_o + other_team_def_rebounds) > 0:
            reb_part = self.or_o / (self.or_o + other_team_def_rebounds)
        else:
            reb_part = 0
        fg_part = self.fga - self.fgm
        return self.fga - reb_part * fg_part * 1.07 + self.to + self.fga * 0.4

class Team:
    def __init__(self, Team_x, data): 
        self.Team_x = Team_x
        self.data = data[(data['Team'] == self.Team_x)]

    def getPointsScored(self):
        return self.data['Points_Scored'].values

    def getPointsAllowed(self):
        return self.data['Points_Allowed'].values

import random as rd
def sim_once(team1,team2):
    score_team1 = rd.gauss(team1.getPointsScored().mean(),team1.getPointsScored().std())
    score_team2 = rd.gauss(team2.getPointsScored().mean(),team2.getPointsScored().std())
    score_against_team1 = rd.gauss(team1.getPointsAllowed().mean(),team1.getPointsAllowed().std())
    score_against_team2 = rd.gauss(team2.getPointsAllowed().mean(),team2.getPointsAllowed().std())
    final_score_t1 = ((score_team1+score_against_team2)/2).round()
    final_score_t2 = ((score_team2+score_against_team1)/2).round()
    if final_score_t1 == final_score_t2:
        sim_once(team1,team2)
    return (final_score_t1,final_score_t2, final_score_t1 > final_score_t2)
    

def sim_multiple(team1,team2,n):
    """Takes two teams in and returns win % of t1, t1 point dist, t2 point dist, win loss binary"""
    t1_points = []
    t2_points = []
    w_l = []
    for i in range(n):
        sim = sim_once(team1,team2)
        t1_points.append(sim[0])
        t2_points.append(sim[1])
        w_l.append(sim[2])
    return (sum(w_l)/n, t1_points, t2_points, w_l)


class simulation:

    def __init__(self, team_1_name, team_2_name, basketball_data):
        self.team_1_name = team_1_name 
        self.team_2_name = team_2_name
        self.basketball_data = basketball_data

    def get_teams(self):
        team_1 = Team(self.team_1_name, self.basketball_data)
        team_2 = Team(self.team_2_name, self.basketball_data)
        return team_1, team_2 

    def run_simulations(self, team_1, team_2):
        sim_out = sim_multiple(team_1, team_2, 10000)
        return sim_out

    def get_frame(self, team_1, team_2, sim_out):
        team_1 = sim_out[1]
        team_1_points = pd.DataFrame(team_1)
        team_1_points = team_1_points.rename(columns = {0 : self.team_1_name})
        team_2 = sim_out[2]
        team_2_points = pd.DataFrame(team_2)
        team_2_points = team_2_points.rename(columns = {0: self.team_2_name})
        monte_carlo_game = [team_1_points, team_2_points]
        monte_carlo_game = pd.concat(monte_carlo_game, axis = 1)
        return monte_carlo_game

    def get_visual(self, monte_carlo_game):
        sns.kdeplot(data=monte_carlo_game, fill = True);
        plt.xlabel('Points Scored')
        plt.ylabel('Frequencey')
        return None 

    def get_full_results(self, sim_out, monte_carlo_game, my_frame_list):
        chances = 100 * sim_out[0]
        team_2_chances = 100 - chances
        my_frame = {}
        my_frame['Team_1'] = self.team_1_name
        my_frame['Team_2'] = self.team_2_name
        my_frame['Team_1_Win_Percent'] = chances 
        my_frame['Team_2_Win_Percent'] = team_2_chances
        my_frame['Team_1_Points'] = monte_carlo_game.loc[0].values.mean()
        my_frame['Team_2_Points'] = monte_carlo_game.loc[1].values.mean()
        final = pd.DataFrame(my_frame, index = [0])
        my_frame_list.append(final)
        return None

    def print_results(self, sim_out, monte_carlo_game):
        print(monte_carlo_game.mean())
        chances = 100 * sim_out[0]
        team_2_chances = 100 - chances
        team_1 = str(f'{self.team_1_name} Win chances: {chances}')
        team_2 = str(f'{self.team_2_name} Win chances: {team_2_chances}')
        return team_1, team_2 
model = pickle.load(open(r'wbb_win_model.pkl', 'rb'))
scaler = pickle.load(open(r'scaler.pkl', 'rb'))

def format_input(fgm, fga, ftm, fta, threepm, threepa, or_o, dr, a, to, st, fgm_a, fga_a, ftm_a, fta_a, threepm_a, threepa_a, or_a, dr_a, a_a, to_a, st_a,  half):
    if half == 1:
        fgm  *= 2
        fga *= 2
        ftm *= 2
        fta *= 2
        threepm *= 2 
        threepa *= 2 
        or_o *= 2 
        dr *= 2 
        a *= 2
        to *= 2 
        st *= 2 
        fgm_a *= 2 
        fga_a *= 2 
        ftm_a *= 2 
        fta_a *= 2 
        threepm_a *= 2 
        threepa_a *= 2 
        or_a *= 2 
        dr_a *= 2 
        a_a *= 2 
        to_a *= 2 
        st_a *= 2 

    tr = or_o + dr
    offensive_stats = advanced_stats(fgm, fga, ftm, fta, threepm, threepa, or_o, dr, a, to, st)
    defensive_stats = advanced_stats(fgm_a, fga_a, ftm_a, fta_a, threepm_a, threepa_a, or_a, dr_a, a_a, to_a, st_a)
    oe = offensive_stats.offensive_efficiency()
    two_ppa = offensive_stats.get_ppa_two()
    three_ppa = offensive_stats.get_ppa_three
    total_ppa = offensive_stats.get_total_ppa()
    s_poss = offensive_stats.team_scoring_poss()
    t_p_poss = offensive_stats.team_play_percent(s_poss)
    poss = offensive_stats.possesions()
    tr_a = or_a + dr_a
    oe_a = defensive_stats.offensive_efficiency()
    two_ppa_a = defensive_stats.get_ppa_two()
    three_ppa_a = defensive_stats.get_ppa_three
    total_ppa_a = defensive_stats.get_total_ppa()
    s_poss_a = defensive_stats.team_scoring_poss()
    t_p_poss_a = defensive_stats.team_play_percent(s_poss)
    poss_a = defensive_stats.possesions()
    return [[fgm, fga, ftm, fta, threepm, threepa, or_o, dr, tr, a, to, st, oe, two_ppa, 
            three_ppa, total_ppa, s_poss, t_p_poss, poss, fgm_a, fga_a, ftm_a, fta_a, threepm_a, threepa_a,
             or_a, dr_a, tr_a, a_a, to_a, st_a, oe_a, two_ppa_a, 
            three_ppa_a, total_ppa_a, s_poss_a, t_p_poss_a, poss_a]]

def model_win_output(input_data):
    input_data = scaler.transform(input_data)
    if round(model.predict_proba(input_data)[0][1] * 100, 2) >= 50:
        return 'Win'
    else:
        return 'Loss'

def win_prob(input_data):
    input_data = scaler.transform(input_data)
    print(input_data)
    return str(round(model.predict_proba(input_data)[0][1] * 100, 2)) + '%'

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('win_predict.html')

@app.route('/win_predict', methods = ['POST'])
def predict():
    int_features = [int(x) for x in request.form.values()]
    final_features = format_input(*int_features)
    this_output = model_win_output(final_features)
    win_pred = win_prob(final_features)
    new_line = '\n'
    return render_template('win_predict.html', prediction_text = f'Win/Loss Prediction: {this_output}', win_percentage = f'Win Probability: {win_pred}')

@app.route('/run_simulations', methods = ['POST'])
def get_sim_data(team_1_name, team_2_name, basketball_data):
    sim_matchup = simulation(team_1_name, team_2_name, basketball_data)
    team_1, team_2 = sim_matchup.get_teams()
    sim_out = sim_matchup.run_simulations(team_1, team_2)
    monte_carlo_game = sim_matchup.get_frame(team_1, team_2, sim_out)
    visual = sim_matchup.get_visual(monte_carlo_game)
    team_1, team_2 = sim_matchup.print_results(sim_out, monte_carlo_game)
    return render_template('simulation.html', plot_url = visual)

if __name__ == '__main__':
    app.run()