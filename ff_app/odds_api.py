
import logging
import os
import json
from datetime import datetime, timedelta

import requests
import pandas as pd

from .config import CONFIG, TEAM_LOOKUP


LOGGER = logging.getLogger()


def get_api_key(path=None):
    """
    """
    path = path or CONFIG['odds_api']['api_key_path']
    path = os.path.expanduser(path)
    assert isinstance(path, str) and os.path.exists(path), path
    
    with open(path, 'r') as f:
        api_key_dict = json.load(f)

    return api_key_dict['API_KEY']


def make_odds_api_call(path=None):
    """
    """
    url = 'https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds'
    params = CONFIG['odds_api']['api_params']
    api_key = get_api_key(path)
    params.update({'api_key': api_key})

    response = requests.get(
        url,
        params=params
    )
    
    assert response.status_code == 200, response

    return response.json()


def create_games_df(data, sportsbook=None):
    """
    """
    sportsbook = sportsbook or CONFIG['odds_api']['sportsbook']

    game_list = []

    for g in data:
        game_dict = {}
        
        game_dict['game_id'] = g['id']
        game_dict['game_time'] = datetime.strptime(
            g['commence_time'], '%Y-%m-%dT%H:%M:%SZ'
        )
        game_dict['home_team'] = g['home_team']
        game_dict['away_team'] = g['away_team']
        
        if sportsbook not in [b['key'] for b in g['bookmakers']]:
            game_dict['last_update'] = None
            game_dict['home_spread_points'] = None
            game_dict['home_spread_price'] = None
            game_dict['away_spread_points'] = None
            game_dict['away_spread_price'] = None
            game_dict['over_points'] = None
            game_dict['over_price'] = None
            game_dict['under_points'] = None
            game_dict['under_price'] = None
        else:
            for b in g['bookmakers']:
                if b['key'] != sportsbook:
                    continue
                
                game_dict['last_update'] = datetime.strptime(
                    b['last_update'], '%Y-%m-%dT%H:%M:%SZ'
                )
                
                for market in b['markets']:
                    if market['key'] == 'spreads':
                        for team in market['outcomes']:
                            if team['name'] == game_dict['home_team']:
                                game_dict['home_spread_points'] = team['point']
                                game_dict['home_spread_price'] = team['price']
                            elif team['name'] == game_dict['away_team']:
                                game_dict['away_spread_points'] = team['point']
                                game_dict['away_spread_price'] = team['price']
                            else:
                                raise
                    elif market['key'] == 'totals':
                        for side in market['outcomes']:
                            if side['name'] == 'Over':
                                game_dict['over_points'] = side['point']
                                game_dict['over_price'] = side['price']
                            elif side['name'] == 'Under':
                                game_dict['under_points'] = side['point']
                                game_dict['under_price'] = side['price']
                            else:
                                raise
                    else:
                        raise
        
        game_list.append(game_dict)
    
    game_df = pd.DataFrame(game_list)

    return game_df


def filter_games_to_week(input_df, week):
    """
    """
    start_date = datetime.today()
    end_date = datetime.strptime(CONFIG['week_end_dates'][week], '%Y-%m-%d')

    filtered_df = input_df[
        (input_df['game_time'] >= start_date) & 
        (input_df['game_time'] <= end_date)
    ].copy()
    
    return filtered_df


def clean_games_df(input_df):
    """
    """
    clean_df = input_df[~input_df['last_update'].isnull()].copy()

    def _favorite(row):
        if row['home_spread_points'] < row['away_spread_points']:
            favorite, underdog = row['home_team'], row['away_team']
        elif row['away_spread_points'] < row['home_spread_points']:
            favorite, underdog =  row['away_team'], row['home_team']
        elif row['home_spread_points'] == row['away_spread_points']:
            favorite, underdog = 'Push', 'Push'
        else:
            favorite, underdog = 'Error', 'Error'
        
        row['favorite'] = favorite
        row['underdog'] = underdog
        
        return row

    clean_df = clean_df.apply(
        _favorite, axis=1
    )

    clean_df['odds_line'] = clean_df.apply(
        lambda x: min(x['home_spread_points'], x['away_spread_points']),
        axis=1
    )
    clean_df['odds_ou'] = clean_df['over_points']

    def _calc_implied_score(row):
        baseline = row['odds_ou'] / 2
        adj = (row['odds_line'] / 2) * -1

        favorite_score = int(baseline + adj)
        underdog_score = int(baseline - adj)

        return str(favorite_score) + " - " + str(underdog_score)

    clean_df['implied_score'] = clean_df.apply(_calc_implied_score, axis=1)

    def _calc_game_desc(row):
        "fav abbrev @/vs dog abbrev"
        if row['away_team'] == row['favorite']:
            location = '@'
        else:
            location = 'vs'
        
        favorite = TEAM_LOOKUP[row['favorite']]['Abbreviation']
        underdog = TEAM_LOOKUP[row['underdog']]['Abbreviation']

        game_str = f'{favorite} {location} {underdog}'

        return game_str

    clean_df['game_desc'] = clean_df.apply(_calc_game_desc, axis=1)

    # Adjust from UTC to US Eastern (offset=-4)
    clean_df['game_time'] = clean_df['game_time'].apply(
        lambda x: x - timedelta(hours=4)
    )
    clean_df.sort_values(by='game_time', inplace=True)
    clean_df.reset_index(drop=True, inplace=True)

    return clean_df


def run(week,
        api_key_path=None,
        sportsbook=None
    ):
    """
    """
    raw_data = make_odds_api_call(api_key_path)
    formatted_data = create_games_df(raw_data, sportsbook)
    filtered_data = filter_games_to_week(formatted_data, week)
    clean_data = clean_games_df(filtered_data)

    return clean_data