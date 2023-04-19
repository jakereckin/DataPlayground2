import pickle
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Offensive efficiency function 
def offensive_efficiency(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers):
   o_e = ((FieldGoalsMade + Assists) / (FieldGoalAttempts + Assists + Turnovers - OffensiveRebounds))
   return o_e

# Efficient Points Scored function 
def efficient_points_scored(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers, PointsScored):
   e_p_s = (offensive_efficiency(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers) * PointsScored)
   return e_p_s

# Raw EOP function 
def raw_EOP(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Turnovers, Assists, PointsScored):
    return (.76 * (Assists + PointsScored) * (offensive_efficiency(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers)))

def game(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers, PointsScored):
   
    return np.array([FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers, 
    offensive_efficiency(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers), 
    efficient_points_scored(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Assists, Turnovers, PointsScored), 
    raw_EOP(FieldGoalAttempts, FieldGoalsMade, OffensiveRebounds, Turnovers, Assists, PointsScored),  PointsScored]).reshape(1,-1)


def predict(game):
    with open('model.bin', 'rb') as f_in:
        model = pickle.load(f_in)
        f_in.close()
    prediction = model.predict(game)
    prediction = pd.DataFrame(prediction)
    prediction = prediction.rename(columns = {0: 'Win or Loss'})
    prediction['Win or Loss'] = prediction['Win or Loss'].apply(lambda x: 'Win' if x == 1 else 'Loss')
    percent_chances = model.predict_proba(game)
    percent_chances = pd.DataFrame(percent_chances)
    percent_chances = percent_chances.rename(columns = {0: 'Loss Percent Chance', 1: 'Win Percent Chance'})
    percent_chances['Loss Percent Chance'] = 100 * percent_chances['Loss Percent Chance']
    percent_chances['Win Percent Chance'] = 100 * percent_chances['Win Percent Chance']
    game_with_percent_chances = [prediction, percent_chances]
    final_prediction = pd.concat(game_with_percent_chances, axis = 1)
    print(final_prediction)


