import pickle
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import eli5
from eli5.sklearn import PermutationImportance
from sklearn.model_selection import train_test_split
from drill_selection import putts_inside_of_ten, up_and_down, round_entry, predict, importance, drill_suggestor, suggest_drills



    
mock_round = round_entry(30, 18, 18, 5, 10, 30, 8, 8)
print(importance(mock_round))
suggest_drills(mock_round)
