"""

"""

import pandas as pd
import numpy as np
import logging

from datetime import datetime

from . import google_io


LOGGER = logging.getLogger(__file__)


def pick_sheet_summary(game_data):
    """
    
    """
    short_df = pd.DataFrame.from_records(
        columns=['Week', 'Datetime', 'Mandatory', 'Favorite', 'Location',
                 'Underdog', 'Spread', 'Total', 'Implied Score'],
        data=game_data.apply(get_short_data, axis=1))
    short_df = short_df[
        ['Week', 'Datetime', 'Mandatory', 'Favorite', 'Location',
         'Underdog', 'Spread', 'Total', 'Implied Score']
    ]
    short_df['Total'] = short_df['Total'].fillna('')
    return short_df


def master_sheet_summary(full_df, short_df):
    """
    
    """
    prep_short_df = short_df.copy()
    prep_short_df.drop(columns=['Week', 'Datetime'], inplace=True)
    combined_df = full_df.reset_index(drop=True).merge(
        prep_short_df, left_index=True, right_index=True)
    combined_df.rename(columns={'home_team': 'Home Team',
                                'away_team': 'Away Team',
                                'odds_line': 'Odds Line',
                                'odds_ou': 'Odds Total',
                                'odds_provider': 'Odds Provider',
                                'venue_name': 'Venue Name',
                                'venue_city_state': 'Venue City',
                                'neutral_site': 'Neutral Site',
                                'conf_game_ind': 'Conference Game',
                                'home_abbr': 'Home Abbr',
                                'away_abbr': 'Away Abbr',
                                'home_record': 'Home Record',
                                'away_record': 'Away Record',
                                'home_rank': 'Home Rank',
                                'away_rank': 'Away Rank',
                                'weather_conditions': 'Weather Conditions',
                                'weather_temp_value': 'Temperature',
                                'networks': 'Networks'
                               }, inplace=True)
    col_list = [
        'Week', 'Datetime', 'Home Team', 'Away Team', 'Networks',
        'Odds Line', 'Odds Total', 'Odds Provider',
        'Venue Name', 'Venue City', 'Neutral Site', 'Conference Game',
        'Home Abbr', 'Home Rank', 'Home Record',
        'Away Abbr', 'Away Rank', 'Away Record',
        'Weather Conditions', 'Temperature',
        'Mandatory', 'Favorite', 'Location',
        'Underdog', 'Spread', 'Total', 'Implied Score'
    ]
    combined_df = combined_df[col_list]
    return combined_df


def create_sheet_outputs(game_data, week_num):
    """
    
    """
    full_df = game_data[game_data['has_odds']].copy()
    full_df['Week'] = week_num
    full_df['Datetime'] = full_df.apply(
        lambda x: datetime.combine(x['date'],
                                   datetime.strptime(x['time'],
                                   '%I:%M %p %Z').time()
                                  ).strftime('%m/%d %I:%M %p (%a)'),
        axis=1)
    full_df.reset_index(drop=True, inplace=True)
    pick_sheet_df = pick_sheet_summary(full_df)
    master_sheet_df = master_sheet_summary(full_df, pick_sheet_df)

    # pick_sheet_df.sort_values(by='Datetime', inplace=True)
    # master_sheet_df.sort_values(by='Datetime', inplace=True)

    return pick_sheet_df, master_sheet_df



def calc_implied_score(spread, total):
    baseline = total / 2
    adj = (spread / 2) * -1
    return {'fav_score': int(baseline + adj),
            'dog_score': int(baseline - adj)}


def implied_score_string(favorite, underdog, spread, total):
    score = calc_implied_score(spread, total)
    s = '{fav} {fav_score} - {dog} {dog_score}' \
        .format(fav=favorite, dog=underdog, **score)
    return s


def get_short_data(row):
    if row['odds_line_fav'] == 'EVEN':
        favorite = row['home_abbr']
        location = 'vs'
        underdog = row['away_abbr']
        spread = 0
    elif row['odds_line_fav'] == row['home_abbr']:
        favorite = row['home_abbr']
        location = 'vs'
        underdog = row['away_abbr']
        spread = row['odds_line_spread']
    elif row['odds_line_fav'] == row['away_abbr']:
        favorite = row['away_abbr']
        location = '@'
        underdog = row['home_abbr']
        spread = row['odds_line_spread']
    else:
        raise ValueError(row)
    
    if not np.isnan(row['odds_ou']):
        try:
            total = row['odds_ou']
            implied_score = implied_score_string(favorite, underdog, spread, total)
        except:
            raise ValueError(row)
    else:
        total = np.nan
        implied_score = ''

    if not np.isnan(row['home_rank']) and not np.isnan(row['away_rank']):
        mandatory = 'Y'
    else:
        mandatory = ''

    week = row['Week']
    datetime = row['Datetime']
    
    return week, datetime, mandatory, favorite, location, \
        underdog, spread, total, implied_score