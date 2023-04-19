from functions import get_date, get_games_from_date, scrape_games, format_data, save_data
from config import Config

if __name__ == '__main__':
    try:
        day_site = Config.site
        game_site = Config.game
        save_file = Config.final_file

        days = get_date()
        formatted = format_data()
        save = save_data(save_file)
        get_games = get_games_from_date(day_site)

        mm_dd_yyyy = days.get_mmddyyyy()
        yyyy_mm_dd = days.get_yyyymmdd()
        games = get_games.get_games(yyyy_mm_dd)
        scrape = scrape_games(game_site, games)
        scraped_data = scrape.scrape_games()
        all_games = formatted.merge_frames(scraped_data)
        save.save_csv(mm_dd_yyyy, all_games)
    except Exception as e:
        print(e)