import pandas as pd, pickle
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.preprocessing import MinMaxScaler

basketball_data = pd.read_csv(r'C:\Users\Jake\Documents\GitHub\FunAnalyticalStuff\hs_wbb_model\Basketball_Final_Stats.csv')
basketball_data_drop_extra = basketball_data.drop(columns = ['Team', 'Game_ID', 'Points_Scored', 'Total Points_Allowed', 'Total Points', 'Points_Allowed', 'Efficient Points Score', 'Raw EOP', 'Efficient Points Score_Allowed', 'Raw EOP_Allowed', 'Offensive_Efficieny_Difference', 'Fouls', 'Technical Fouls', 'Fouls_Allowed',
       'Technical Fouls_Allowed', 'Blocks', 'Blocks_Allowed'])
y = basketball_data_drop_extra['Win']
X = basketball_data_drop_extra.drop(columns = ['Win'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .2, random_state = 13)
scaled = MinMaxScaler().fit(X_train)
X_train_scaled = scaled.transform(X_train)
X_test_scaled = scaled.transform(X_test)
knn = KNeighborsClassifier(n_neighbors = 10)
knn_fit = knn.fit(X_train_scaled, y_train)
pickle.dump(knn_fit, open(r'C:\Users\Jake\Documents\GitHub\FunAnalyticalStuff\hs_wbb_model\wbb_win_model.pkl', 'wb'))
pickle.dump(scaled, open(r'C:\Users\Jake\Documents\GitHub\FunAnalyticalStuff\hs_wbb_model\scaler.pkl', 'wb'))