from win_predictor import offensive_efficiency, efficient_points_scored, raw_EOP, game, predict
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

game = game(36, 15, 13, 19, 5, 45)

prediction = predict(game)