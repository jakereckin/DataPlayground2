import time
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
import pandas as pd 
import re
import requests 
from bs4 import BeautifulSoup as bs 
from selenium.webdriver.common.by import By
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

class get_date:

    def __init__(self):
        return None 

    def get_yyyymmdd(self):
        date = dt.datetime.today() - dt.timedelta(days = 2)
        date = date.strftime('%Y/%m/%d')
        return date 

    def get_mmddyyyy(self):
        date = dt.datetime.today() - dt.timedelta(days = 2)
        date = date.strftime('%m_%d_%Y')
        return date 

class get_games_from_date:

    def __init__(self, site):
        self.site = site 
        return None 

    def get_games(self, date):
        '''
        date : yyyy/mm/dd
        '''
        print(f'Getting Games for {date}')
        day_site = self.site.replace('~DATE~', date)
        page = requests.get(day_site)
        soup = bs(page.content, 'html.parser')
        game_list = soup.find_all('tr', id = lambda x: x and x.startswith('game_list_row_'))
        games = []
        for result in game_list:
            game = str(result).split('>')[0].replace('"', '')[-8:]
            games.append(game)
        return games 

class scrape_games:
    
    def __init__(self, site, games):
        self.site = site 
        self.games = games 
        return None 

    def scrape_games(self):
        total_start = time.perf_counter()
        full_frames = []
        succes_count = 0
        error_count = 0
        for this in self.games:
            try:
                start = time.perf_counter()
                driver = webdriver.Chrome(ChromeDriverManager().install())
                search = self.site.replace('~GAME_ID~', this)
                driver.get(search)
                driver.maximize_window()
                time.sleep(5)
                driver.find_element(By.ID, 'tab_gs3_game_stats').click()
                time.sleep(10)
                team_stats = driver.find_element(By.CLASS_NAME, 'StatWidgetHolder')
                team_names = driver.find_element(By.CLASS_NAME, 'team_box')
                my_data = team_stats.text.strip()
                my_teams = team_names.text.strip()
                driver.close()
                my_teams_data = my_teams.split('\n')
                game_dict = {}
                points_score = []
                teams = []
                for data in my_teams_data:
                    points_score.append(data.rsplit(' ', 1)[1])
                    teams.append(data.rsplit(' ', 1)[0])
                game_overview = {}
                game_overview['Team_Name'] = teams
                game_overview['Points_Scored'] = points_score
                game_overview['Game_ID'] = [str(this), str(this)]
                game = pd.DataFrame(game_overview)
                game_stats = my_data.replace('\n', ' ').replace('SCORING STATS', '').replace('REBOUNDS STATS', '').replace('MISC STATS', '').strip()
                game_stats_only = re.findall('[0-9]+', game_stats)
                game_stats_headers = re.findall(r'\D+', game_stats)
                stat_headers = []
                for stat in game_stats_headers:
                    this_stat = stat.strip()
                    if this_stat != '':
                        stat_headers.append(this_stat)

                game_stats_grouped = [game_stats_only[stat : stat + 2] for stat in range(0, len(game_stats_only), 2)]
                game_stats = {}
                for stat in stat_headers:
                    team_dict = {}
                    this_index = stat_headers.index(stat)
                    team_dict[stat] = game_stats_grouped[this_index]
                    game_stats.update(team_dict)

                my_frame = pd.DataFrame(game_stats)
                full_game = pd.concat([game, my_frame], axis = 1)
                full_frames.append(full_game)
                end = time.perf_counter()
                succes_count += 1
                print(str(this) + ': Time taken, ' + str(end - start) + ' success')
            except Exception as e:
                print(e)
                try:
                    driver.close()
                except Exception:
                    continue
                error_count +=1
        total_end = time.perf_counter()
        print(str(total_end - total_start))
        print('Errors: ' + str(error_count))
        print('Success: ' + str(succes_count))
        return full_frames 

class format_data:

    def __init__(self):
        return None 

    def merge_frames(self, full_frames):
        all_games = pd.concat(full_frames)
        return all_games 

class save_data:

    def __init__(self, file):
        self.file = file 
        return None 

    def save_csv(self, date, all_games):
        '''
        date : 'mm/dd/yyyy
        
        '''
        date_file = self.file.replace('~DATE~', date)
        all_games.to_csv(date_file, index = False)
        return None 