"""
"""
import os
import sys
import logging

from . import scrape_espn, data_prep, google_io
from .config import CONFIG


LOGGER = logging.getLogger(__file__)


def run_data_pull(week, year=None, output_dir=None, return_all_games=False):
    """
    Execute data pull from ESPN and create data frames for game views

    Parameters
    ----------
    week : int
        Week number within the season (eg. opening week is 1)

    year : int (default None)
        Year for the current season

    output_dir : str (default None)
        Path to which game data CSV files are saved

    return_all_games : bool (default False)
        Indicator for whether all games should be returned. If False,
        only games with spreads will be returned; otherwise, if True,
        all games will be returned regardless of spread

    Returns
    -------
    picks_view : pandas.DataFrame
        Dataframe containing the picks data for upload to individual's
        pickem sheets

    full_data : pandas.DataFrame
        Dataframe containing the full set of game data (for games with
        a spread) for a single week, to be uploaded to the main game data sheet

    games : pandas.DataFrame
        Dataframe containing the full data for all games in a single week,
        regardless of whether they have a spread. Only returned in cases
        where `return_all_games` is passed `False`
    """
    year = year or CONFIG['games']['year']
    output_dir = output_dir \
        or os.path.join(os.path.expanduser(CONFIG['output']), str(year))
    
    pull = scrape_espn.GetGameData(week_num=week, year=year)
    games = pull.game_data_df
    LOGGER.info("Pulled %s total games for week %s in %s",
                len(games), week, year)
    LOGGER.info("%s games have odds available",
                sum(games['has_odds']))

    picks_view, full_data = data_prep.create_sheet_outputs(games, week)
    LOGGER.info("Picks sheet data has shape %s", picks_view.shape)
    LOGGER.info("Game list data has shape %s", full_data.shape)

    output_path = os.path.join(output_dir, f'week{week}.csv')
    LOGGER.info("Saving game data to disk at '%s'", output_path)
    full_data.to_csv(output_path, index=False)

    if return_all_games:
        return picks_view, full_data, games
    else:
        return picks_view, full_data


def update_google_sheet(picks_view, full_data, player_list=None):
    """
    Performs the API call to Google Sheets for uploading the games data
    to the main game data sheet and each individual player's pickem sheet

    Parameters
    ----------
    picks_view : pandas.DataFrame
        Dataframe containing the picks view of games for a single week
        for upload to each individual's pickem sheet
    
    full_data : pandas.DataFrame
        Dataframe containing the full set of details for all games with
        a spread for a single week, to be uploaded to the main game sheet

    player_list : list (default None)
        List of players making picks; this should correspond directly to
        the names of the individual sheets where pickem views are uploaded

    Returns
    -------
    None
    """
    io = google_io.GoogleSheetsReadWrite()

    picks_df = picks_view.copy()
    for col in picks_df.columns:
        picks_df[col] = picks_df[col].fillna('').astype(str)

    full_df = full_data.copy()
    for col in full_df.columns:
        full_df[col] = full_df[col].fillna('').astype(str)

    players = player_list or CONFIG['player_list']
    for p in players:
        LOGGER.info("Writing data for %s", p)
        io.write(p, picks_df)

    LOGGER.info("Writing out game list")
    io.write('Game List', full_df)


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'No week number provided'
    week_num = sys.argv[1]

    LOGGER.info("Executing data pull and upload for week %s", week_num)
    short_df, combined_df = run_data_pull(week=week_num)
    update_google_sheet(short_df, combined_df)
    LOGGER.info("Execution complete")

