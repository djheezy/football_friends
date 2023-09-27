"""
Prepares the raw data pulled by the scraper into dataframes that are
ready to be uploaded to the pick em Google sheet
"""
import pandas as pd
import numpy as np
import logging

from datetime import datetime

from . import google_io

LOGGER = logging.getLogger(__file__)


def pick_sheet_summary(game_data):
    """
    Produce a short dataframe of game data for upload to individual
    group members' sheets. This view contains the columns for the
    game week and date; indicator for whether the game is a mandatory
    pick; odds favorite, underdog, spread, total, and implied score;
    and location of the game.

    Parameters
    ----------
    game_data : pandas.DataFrame
        Dataframe containing the full game data for a single week of
        games as scraped from ESPN
    
    Returns
    -------
    short_df : pandas.DataFrame
        Dataframe containing the individual picks view of game data
    """
    short_df = game_data.copy()
    short_df.rename(
        columns={
            'week': 'Week',
            'home_team': 'Home Team',
            'away_team': 'Away Team',
            'favorite': 'Favorite',
            'underdog': 'Underdog',
            'odds_line': 'Spread',
            'odds_ou': 'Total',
            'game_desc': 'Description',
            'implied_score': 'Implied Score'
        },
        inplace=True
    )
    short_df['Mandatory'] = 'N'

    short_df = short_df[
        ['Week', 'Datetime', 'Mandatory', 'Home Team', 'Away Team',
         'Favorite', 'Underdog', 'Description', 'Spread', 'Total', 'Implied Score']
    ]
    short_df['Total'] = short_df['Total'].fillna('')
    return short_df


def create_sheet_outputs(game_data, week_num):
    """
    
    """
    full_df = game_data.copy()
    full_df['Week'] = week_num
    full_df['Datetime'] = full_df.apply(
        lambda x: x['game_time'].strftime('%m/%d %I:%M %p (%a)'),
        axis=1
    )
    full_df.reset_index(drop=True, inplace=True)
    pick_sheet_df = pick_sheet_summary(full_df)

    return pick_sheet_df
