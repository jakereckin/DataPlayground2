import pickle
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import eli5
from eli5.sklearn import PermutationImportance
from sklearn.model_selection import train_test_split
# Defining percentage functions 
def putts_inside_of_ten(PuttsInsideTenFeetAttempted, PuttsInsideTenFeetMade):
    ten_feet_percentage = (100 * (PuttsInsideTenFeetMade / PuttsInsideTenFeetAttempted))
    return ten_feet_percentage

def up_and_down(UpAndDownAttempts, UpAndDownSuccess):
    up_and_down_percentage = (100 * (UpAndDownSuccess / UpAndDownAttempts))
    return up_and_down_percentage

# Input of round
def round_entry(Putts, PuttsInsideTenFeetAttempted, PuttsInsideTenFeetMade, Fairways, Greens, Inside100, UpAndDownAttempts, UpAndDownSuccess):
    PuttsInsideTenFeetMakePercentage = putts_inside_of_ten(PuttsInsideTenFeetAttempted, PuttsInsideTenFeetMade)
    UpAndDownSuccessPercentage = up_and_down(UpAndDownAttempts, UpAndDownSuccess)
    return np.array([Putts, PuttsInsideTenFeetAttempted, PuttsInsideTenFeetMade, PuttsInsideTenFeetMakePercentage, Fairways, 
    Greens, Inside100, UpAndDownAttempts, UpAndDownSuccess, UpAndDownSuccessPercentage]).reshape(1,-1)


def predict(round_x):
    with open('model.golf', 'rb') as f_in:
        model = pickle.load(f_in)
        f_in.close()
    prediction = model.predict(round_x)
    prediction = pd.DataFrame(prediction)
    prediction = prediction.rename(columns = {0: 'Above or Below'})
    prediction['Above or Below'] = prediction['Above or Below'].apply(lambda x: 'Above' if x == 1 else 'Below')
    percent_chances = model.predict_proba(round_x)
    percent_chances = pd.DataFrame(percent_chances)
    percent_chances = percent_chances.rename(columns = {0 :'% chance of Below Average', 1: '% chance of Above Average'})
    game_with_percent_chances = [prediction, percent_chances]
    final_prediction = pd.concat(game_with_percent_chances, axis = 1)
    return final_prediction

def importance(round_x):
    with open('model.golf', 'rb') as f_in:
        model = pickle.load(f_in)
        f_in.close()
    golf_scores = pd.read_csv('jake_golf_scores.csv')
    golf_scores_num = golf_scores.drop(columns = 'DateOfRound')
    # Create new data frame for comparison to average
    golf_scores_with_average = golf_scores.copy()
    golf_scores_with_average['AverageScore'] = golf_scores_with_average.Score.mean()
    golf_scores_with_average['AboveOrBelowAverage'] = golf_scores_with_average.Score > golf_scores_with_average.AverageScore
    # Above or below average column changed to when above average = 1 and below average = 0
    golf_scores_with_average['AboveOrBelowAverage'] = golf_scores_with_average['AboveOrBelowAverage'].astype(int)
    golf_scores_with_average_num = golf_scores_with_average.drop(columns = ['DateOfRound'])
    base_features2 = ['Putts', 'PuttsInsideTenFeetAttempted', 'PuttsInsideTenFeetMade', 'PuttsInsideTenFeetMakePercentage', 'Fairways', 'Greens', 'Inside100', 'UpAndDownAttempts', 'UpAndDownSuccess', 'UpAndDownSuccessPercentage']
    X = golf_scores_with_average_num[base_features2]
    y = golf_scores_with_average_num.AboveOrBelowAverage
    train_X, val_X, train_y, val_y = train_test_split(X, y, train_size = 0.8, test_size = 0.2, random_state = 1)
    model.fit(train_X, train_y)
    importances = pd.DataFrame(abs(model.coef_))
    importances = importances.transpose()
    importances = importances.rename(index = {0 : 'Putts', 1: 'PuttsInsideTenFeetAttempted', 2: 'PuttsInsideTenFeetMade', 3:'PuttsInsideTenFeetMakePercentage' ,4: 'Fairways' , 5: 'Greens' , 6: 'Inside100'  ,7: 'UpAndDownAttempts' ,8: 'UpAndDownSuccess' , 9: 'UpAndDownSuccessPercentage' })
    #importances = importances.sort_values(by = [0], ascending = False)
    X_averages = X.mean()
    importances = importances.rename(columns = {0: 'Weights'})
    averages_with_weights = [importances, X_averages]
    averages_with_weights = pd.concat(averages_with_weights, axis = 1)
    averages_with_weights = averages_with_weights.rename(columns = {0 : 'Averages'})
    averages_with_weights = averages_with_weights.sort_values(by = 'Weights', ascending = False)
    round_data = round_x.reshape(-1,1)
    round_data = pd.DataFrame(round_data)
    round_data = round_data.rename(index = {0 : 'Putts', 1: 'PuttsInsideTenFeetAttempted', 2: 'PuttsInsideTenFeetMade', 3:'PuttsInsideTenFeetMakePercentage' ,4: 'Fairways' , 5: 'Greens' , 6: 'Inside100'  ,7: 'UpAndDownAttempts' ,8: 'UpAndDownSuccess' , 9: 'UpAndDownSuccessPercentage' })
    averages_with_weights_with_round = [averages_with_weights, round_data]
    averages_with_weights_with_round = pd.concat(averages_with_weights_with_round, axis = 1)
    averages_with_weights_with_round = averages_with_weights_with_round.rename(columns = {0 : 'Your Round'})
    averages_with_weights_with_round['Round Difference'] = averages_with_weights_with_round['Your Round'] - averages_with_weights_with_round['Averages']
    return averages_with_weights_with_round
     
  
def drill_suggestor(round_x):
    your_game = importance(round_x)
    if your_game.iloc[0,3] < 0 and your_game.iloc[1,3] < 0 and your_game.iloc[7,3] < 0 and your_game.iloc[8,3] < 0 and your_game.iloc[4,3] < 0 and your_game.iloc[5,3] > 0 and your_game.iloc[6,3] > 0 and your_game.iloc[9,3] > 0: 
        print("Work on everything")
    elif your_game.iloc[0,3] > 0 and your_game.iloc[1,3] > 0  and your_game.iloc[7,3] > 0 and your_game.iloc[8,3] > 0 and your_game.iloc[4,3] > 0 and your_game.iloc[5,3] < 0 and your_game.iloc[6,3] < 0 and your_game.iloc[9,3] < 0:
        print("Great day!")
    else:
        if your_game.iloc[0, 3] < 0:
            print("Work on chipping")
        elif your_game.iloc[1, 3] < 0:
            print("Work on irons")
        elif your_game.iloc[4,3] < 0:
            print("Hit the ball closer into the green")
        elif your_game.iloc[5,3] > 0:
            print("Hit more greens")
        elif your_game.iloc[6, 3] > 0:
            print("Make more putts")
        elif your_game.iloc[7, 3] < 0:
            print("Make more putts inside ten feet")
        elif your_game.iloc[8, 3] < 0:
            print("Hit driver straighter")
        elif your_game.iloc[9, 3] > 0:
            print("Work on wedges")


def suggest_drills(round_x):
    def up_and_down_percentage(round_x):
        your_game = importance(round_x)
        UpAndDownSuccessPercentage = your_game.loc[['UpAndDownSuccessPercentage'], ['Round Difference']].values
        if UpAndDownSuccessPercentage > 50:
            pass
        else:
            if UpAndDownSuccessPercentage < 50 and UpAndDownSuccessPercentage > 25:
                suggestion = "Good day, but can be better!"
            elif UpAndDownSuccessPercentage < 25 and UpAndDownSuccessPercentage > 0:
                suggestion = "Slightly above average, keep working"
            elif UpAndDownSuccessPercentage == 0:
                suggestion = "Right at your average"
            elif UpAndDownSuccessPercentage < 0 and UpAndDownSuccessPercentage > -25:
                suggestion = "Slightly below average, work harder"
            elif UpAndDownSuccessPercentage < -25 and UpAndDownSuccessPercentage > -50:
                suggestion = "Really bad day, focus on this"
            print(suggestion)

    def greens_hit(round_x):
        your_game = importance(round_x)
        Greens = your_game.loc[['Greens'], ['Round Difference']].values
        if Greens < 7 and Greens > 3:
            pass
        else:
            if Greens < 3 and Greens > 0:
                suggestion = "You hit the ball slightly above average today"
            elif Greens < 0 and Greens > -3:
                suggestion = "You hit the ball slightly below average today"
            elif Greens < -3 and Greens > -7:
                suggestion = "You hit the ball poorly today"
            elif Greens < -7:
                suggestion = "Wow, that was terrible"
            print(suggestion)

    def putts_inside_ten_made(round_x):
        your_game = importance(round_x)
        PuttsInsideTenFeetMade = your_game.loc[['PuttsInsideTenFeetMade'], ['Round Difference']].values
        if PuttsInsideTenFeetMade > 0 and PuttsInsideTenFeetMade < 1.1:
            suggestion = 'Made slightly more putts inside 10 feet'
        elif PuttsInsideTenFeetMade > 1.1:
            suggestion = 'Made more putts today inside of 10 feet'
        elif PuttsInsideTenFeetMade > -2 and PuttsInsideTenFeetMade < 0:
            suggestion = 'Made less putts today inside of 10 feet'
        else:
            suggestion = 'Hit the ball closer or you chipped in a shit ton'
        print(suggestion)

    def up_and_down_success(round_x):
        your_game = importance(round_x)
        UpAndDownSuccess = your_game.loc[['UpAndDownSuccess'], ['Round Difference']].values
        if UpAndDownSuccess > 2 and UpAndDownSuccess < 5:
            suggestion = 'You either hit less greens, or got up and down a lot'
        elif UpAndDownSuccess > 5:
            suggestion = 'You missed greens but got up and down a lot'
        elif UpAndDownSuccess < 1 and UpAndDownSuccess > -1:
            suggestion = 'Average day getting up and down'
        elif UpAndDownSuccess < -1 and UpAndDownSuccess > -3:
            suggestion = 'You either hit a lot of greens or did not get up and down a lot'
        else:
            suggestion = 'Can not interpret round data'
        print(suggestion)

    def putts_inside_ten_attempted(round_x):
        your_game = importance(round_x)
        PuttsInsideTenFeetAttempted = your_game.loc[['PuttsInsideTenFeetAttempted'], ['Round Difference']].values
        if PuttsInsideTenFeetAttempted > 0 and PuttsInsideTenFeetAttempted < 5:
            suggestion = 'You hit the ball really close today, or missed a lot of putts inside ten feet'
        elif PuttsInsideTenFeetAttempted < 0 and PuttsInsideTenFeetAttempted > -5:
            suggestion = 'You did not hit the ball close today, or made a lot of putts inside ten feet'
        else:
            suggestion = 'Can not give feedback with this data'
        print(suggestion) 

    def up_and_down_attempts(round_x):
        your_game = importance(round_x)
        UpAndDownAttempts = your_game.loc[['UpAndDownAttempts'], ['Round Difference']].values
        if UpAndDownAttempts < 0:
            suggestion = 'You hit more greens today'
        else:
            suggestion = 'Focus on hitting more greens next round'
        print(suggestion)

    def putts(round_x):
        your_game = importance(round_x)
        Putts = your_game.loc[['Putts'], ['Round Difference']].values
        if Putts < -3:
            pass
        else:
            if Putts > 0 and Putts < 3:
                suggestion = 'More putts today, focus on speed control or putts inside ten feet'
            elif Putts > 3 and Putts < 5:
                suggestion = 'Really below average putting day, focus on this more in practice'
            elif Putts > 5:
                suggestion = 'Absolutley terrible day putting'
            elif Putts < 0 and Putts > -3:
                suggestion = 'Above average day of putting, but room to grow'
            print(suggestion)
        
    def putts_inside_ten_percentage(round_x):
        your_game = importance(round_x)
        PuttsInsideTenFeetMakePercentage = your_game.loc[['PuttsInsideTenFeetMakePercentage'], ['Round Difference']].values
        if PuttsInsideTenFeetMakePercentage > 10:
            pass
        else:
            if PuttsInsideTenFeetMakePercentage > 0 and PuttsInsideTenFeetMakePercentage < 10:
                suggestion = 'Above average day putting inside ten feet, but room to improve'
            elif PuttsInsideTenFeetMakePercentage < 0 and PuttsInsideTenFeetMakePercentage > -5:
                suggestion = 'Slightly below average day putting inside ten feet, work a little more on this'
            elif PuttsInsideTenFeetMakePercentage < -5 and PuttsInsideTenFeetMakePercentage > -20:
                suggestion = 'Really below average day putting, focus on this in practice'
            else:
                suggestion = 'Quit golf'
            print(suggestion)

    def fairways(round_x):
        your_game = importance(round_x)
        Fairways = your_game.loc[['Fairways'] , ['Round Difference']].values
        if Fairways > 3:
            pass
        else:
            if Fairways > 0 and Fairways < 3:
                suggestion = 'Slightly above average day off the tee, but room to improve'
            elif Fairways < 0 and Fairways > -3:
                suggestion = 'Slightly below average day off the tee, focus on this in practice'
            else:
                suggestion = 'Terrible day, really work on this'
            print(suggestion)

    def inside_100(round_x):
        your_game = importance(round_x)
        Inside100 = your_game.loc[['Inside100'], ['Round Difference']].values
        if Inside100 > 0 and Inside100 < 5:
            suggestion = 'Below average day inside 100, focus on this in practice'
        elif Inside100 > 5:
            suggestion = 'Really bad day, make this is a priority in practice'
        elif Inside100 < 0 and Inside100 > -4:
            suggestion = 'Slighly above average day inside 100, but still room to improve'
            print(suggestion)
        else:
            pass

    print()
    up_and_down_percentage(round_x)
    print()
    greens_hit(round_x)
    print()
    putts_inside_ten_made(round_x)
    print()
    up_and_down_success(round_x)
    print()
    putts_inside_ten_attempted(round_x)
    print()
    up_and_down_attempts(round_x)
    print()
    putts(round_x)
    print()
    putts_inside_ten_percentage(round_x)
    print()
    fairways(round_x)
    print()
    inside_100(round_x)
    print()

