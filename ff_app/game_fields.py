
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import pytz


def get_home_team(game):
    try:
        return game['competitions'][0]['competitors'][0]['team']['displayName']
    except:
        return ''


def get_away_team(game):
    try:
        return game['competitions'][0]['competitors'][1]['team']['displayName']
    except:
        return ''


def get_home_abbr(game):
    try:
        return game['competitions'][0]['competitors'][0]['team']['abbreviation']
    except:
        return ''


def get_away_abbr(game):
    try:
        return game['competitions'][0]['competitors'][1]['team']['abbreviation']
    except:
        return ''


def get_game_date(game):
    try:
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.utc

        return utc.localize(dt.strptime(game['competitions'][0]['startDate'], '%Y-%m-%dT%H:%MZ')).astimezone(eastern).date()
    except:
        return ''


def get_game_time(game):
    try:
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.utc

        return utc.localize(dt.strptime(game['competitions'][0]['startDate'], '%Y-%m-%dT%H:%MZ')).astimezone(eastern).strftime('%I:%M %p %Z')
    except:
        return ''


def get_game_odds_line(game):
    try:
        return game['competitions'][0]['odds'][0]['details']
    except:
        return None


def has_odds(game):
    try:
        return 'odds' in game['competitions'][0]
    except:
        return None


def get_game_odds_ou(game):
    try:
        return game['competitions'][0]['odds'][0]['overUnder']
    except:
        return None


def get_game_odds_provider(game):
    try:
        return game['competitions'][0]['odds'][0]['provider']['name']
    except:
        return ''


def parse_game_odds_line(odds_line):
    try:
        if odds_line == 'EVEN':
            return odds_line, 0
        else:
            favorite = odds_line.split(' ', 1)[0]
            spread = float(odds_line.split(' ', 1)[1])
            return favorite, spread
    except:
        return None, None


def get_game_networks(game):
    try:
        return game['competitions'][0]['broadcasts'][0]['names']
    except:
        return []


def get_neutral_site_ind(game):
    try:
        return game['competitions'][0]['neutralSite']
    except:
        return None


def get_game_weather_conditions(game):
    # return game['competitions'][0]['weather']['conditions'],game['competitions'][0]['weather']['highTemperature']
    try:
        return game['weather']['displayValue']
    except:
        return ''


def get_game_weather_temp(game):
    # return game['competitions'][0]['weather']['conditions'],game['competitions'][0]['weather']['highTemperature']
    try:
        return 'High', game['weather']['highTemperature']
    except:
        try:
            return 'Low', game['weather']['lowTemperature']
        except:
            return ('', '')


def get_venue_name(game):
    try:
        return game['competitions'][0]['venue']['fullName']
    except:
        return ''


def get_venue_city(game):
    try:
        return game['competitions'][0]['venue']['address']['city']
    except:
        return ''


def get_venue_state(game):
    try:
        return game['competitions'][0]['venue']['address']['state']
    except:
        return ''


def get_home_record(game):
    try:
        return game['competitions'][0]['competitors'][0]['records'][0]['summary']
    except:
        return ''


def get_away_record(game):
    try:
        return game['competitions'][0]['competitors'][1]['records'][0]['summary']
    except:
        return ''


def get_conf_game_ind(game):
    try:
        return game['competitions'][0]['conferenceCompetition']
    except:
        return None


def get_home_score(game):
    try:
        return game['competitions'][0]['competitors'][0]['score']
    except:
        return 0


def get_away_score(game):
    try:
        return game['competitions'][0]['competitors'][1]['score']
    except:
        return 0


def get_game_finish(game):
    try:
        return game['competitions'][0]['status']['type']['completed']
    except:
        return None


def get_game_started(game):
    try:
        return game['competitions'][0]['status']['period'] > 0
    except:
        return None


def get_game_quarter(game):
    try:
        return game['competitions'][0]['status']['period']
    except:
        return ''


def get_game_clock(game):
    try:
        return game['competitions'][0]['status']['displayClock']
    except:
        return ''


def get_home_rank(game):
    try:
        rank = game['competitions'][0]['competitors'][0]['curatedRank']['current']
        if rank <= 25 and rank > 0:
            return rank
        else:
            return None
    except:
        return None


def get_away_rank(game):
    try:
        rank = game['competitions'][0]['competitors'][1]['curatedRank']['current']
        if rank <= 25 and rank > 0:
            return rank
        else:
            return None
    except:
        return None
