
# import pandas
import importlib
import requests
import json
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import logging

from . import game_fields

from .config import CONFIG


LOGGER = logging.getLogger(__file__)


class GetGameData():
    '''
    To Do:
     - team stats?
     - game link?

     - Export to csv/excel/google sheets?
    '''
    def __init__(self, week_num, year):
        self.week_num = week_num
        self.year = year
        return

    # Bowl-specific URL
    @property
    def scrape_url(self):
        if self.week_num == 'bowls':
            url = CONFIG['games']['url']['bowls'].format(year=self.year)
        else:
            url = CONFIG['games']['url']['inseason'].format(year=self.year, week=self.week_num)
        return url

    @property
    def request(self):
        r = requests.get(self.scrape_url)
        return r

    def find_script_index(self, soup_scripts):
        for i, s in enumerate(soup_scripts):
            if 'competitions' in str(s):
                return i
        else:
            return 13

    @property
    def request_data(self, request_instance=None):
        request = request_instance or self.request
        soup = bs(request.text, "html5lib")
        soup_scripts = soup.select('script')
        s_index = self.find_script_index(soup_scripts)
        score_data = str(soup_scripts[s_index]).split('=', 1)[1].lstrip(' ').replace(';</script>', '').replace('&#39;', "'").split(';window', 1)[0]

        return json.loads(score_data)

    def save_data_to_file(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        return None

    @property
    def all_games_dict(self, request_data=None):
        data = request_data or self.request_data

        games = data['events']

        game_dict = {}
        for i, game in enumerate(games):
            game_info = {'date': game_fields.get_game_date(game),
                         'time': game_fields.get_game_time(game),
                         'networks': str(game_fields.get_game_networks(game)).replace('u', '').strip('[]').replace("'", "").replace('ABC, ESPN3', 'ABC'),
                         'home_team': game_fields.get_home_team(game),
                         'home_abbr': game_fields.get_home_abbr(game),
                         'away_team': game_fields.get_away_team(game),
                         'away_abbr': game_fields.get_away_abbr(game),
                         'has_odds': game_fields.has_odds(game),
                         'odds_provider': game_fields.get_game_odds_provider(game),
                         'odds_line': game_fields.get_game_odds_line(game),
                         'odds_line_fav': game_fields.parse_game_odds_line(game_fields.get_game_odds_line(game))[0],
                         'odds_line_spread': game_fields.parse_game_odds_line(game_fields.get_game_odds_line(game))[1],
                         'odds_ou': game_fields.get_game_odds_ou(game),
                         'neutral_site': game_fields.get_neutral_site_ind(game),
                         'weather_conditions': game_fields.get_game_weather_conditions(game),
                         'weather_temp_type': game_fields.get_game_weather_temp(game)[0],
                         'weather_temp_value': game_fields.get_game_weather_temp(game)[1],
                         'venue_name': game_fields.get_venue_name(game),
                         'venue_city': game_fields.get_venue_city(game),
                         'venue_state': game_fields.get_venue_state(game),
                         'venue_city_state': game_fields.get_venue_city(game) + ', ' + game_fields.get_venue_state(game),
                         'home_record': game_fields.get_home_record(game),
                         'away_record': game_fields.get_away_record(game),
                         'conf_game_ind': game_fields.get_conf_game_ind(game),
                         'home_score': game_fields.get_home_score(game),
                         'away_score': game_fields.get_away_score(game),
                         'home_rank': game_fields.get_home_rank(game),
                         'away_rank': game_fields.get_away_rank(game),
                         'game_started': game_fields.get_game_started(game),
                         'game_complete': game_fields.get_game_finish(game),
                         'game_quarter': game_fields.get_game_quarter(game),
                         'game_clock': game_fields.get_game_clock(game)
                         }
            game_dict[i] = game_info

        return game_dict

    @property
    def game_data_dict(self, game_dict=None):
        games = game_dict or self.all_games_dict
        return games
        # odds_games = {}
        # for i in games:
        #     if games[i]['has_odds']:
        #         odds_games[i] = games[i]
        # return odds_games

    @property
    def game_dict_completed(self, game_dict=None):
        games = game_dict or self.game_data_dict
        completed_games = {}
        for i in games:
            if games[i]['game_complete']:
                completed_games[i] = games[i]
        return completed_games

    @property
    def game_dict_inprogress(self, game_dict=None):
        games = game_dict or self.game_data_dict
        inprogress_games = {}
        for i in games:
            if games[i]['game_started']:
                inprogress_games[i] = games[i]
        return inprogress_games

    @property
    def game_dict_upcoming(self, game_dict=None):
        games = game_dict or self.game_data_dict
        upcoming_games = {}
        for i in games:
            if (not games[i]['game_started']) and (not games[i]['game_complete']):
                upcoming_games[i] = games[i]
        return upcoming_games

    @property
    def game_data_df(self, game_dict=None):
        pandas = importlib.import_module('pandas')
        games = game_dict or self.game_data_dict
        game_df = pandas.DataFrame.from_dict(games, orient='index')
        return game_df
