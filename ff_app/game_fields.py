
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import pytz


def get_home_team(game):
    try:
        value = game['teams'][0]['displayName']
    except:
        value = ''
    return value

def get_away_team(game):
    try:
        value = game['teams'][1]['displayName']
    except:
        value = ''
    return value

def get_home_abbr(game):
    try:
        value = game['teams'][0]['abbrev']
    except:
        value = ''
    return value


def get_away_abbr(game):
    try:
        value = game['teams'][1]['abbrev']
    except:
        value = ''
    return value


def get_game_date(game):
    try:
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.utc

        value = utc.localize(dt.strptime(game['date'], '%Y-%m-%dT%H:%MZ')).astimezone(eastern).date()
    except:
        value = ''
    return value


def get_game_time(game):
    try:
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.utc

        value = utc.localize(dt.strptime(game['date'], '%Y-%m-%dT%H:%MZ')).astimezone(eastern).strftime('%I:%M %p %Z')
    except:
        value = ''
    return value


def get_game_odds_line(game):
    try:
        value = game['odds']['details']
    except:
        value = None
    return value


def has_odds(game):
    try:
        value = ('odds' in game) & ('details' in game['odds'])
    except:
        value = None
    return value


def get_game_odds_ou(game):
    try:
        value = game['odds']['oU']
    except:
        value = None
    return value


def get_game_odds_provider(game):
    try:
        value = game['odds']['pvdr']
    except:
        value = ''
    return value


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


def parse_game_odds_ou(game):
    odds_ou = get_game_odds_ou(game)
    try:
        return float(odds_ou.split(' : ')[1])
    except:
        return None


def get_game_networks(game):
    try:
        return game['broadcasts']['name']
    except:
        return []


def get_neutral_site_ind(game):
    # No longer supported on ESPN scape
    return None


def get_game_weather_conditions(game):
    try:
        return game['wthr']['displayValue']
    except:
        return ''


def get_game_weather_temp(game):
    try:
        return 'High', game['wthr']['highTemperature']
    except:
        try:
            return 'Low', game['wthr']['lowTemperature']
        except:
            return ('', '')


def get_venue_name(game):
    try:
        return game['vnue']['fullName']
    except:
        return ''


def get_venue_city(game):
    try:
        return game['vnue']['address']['city']
    except:
        return ''


def get_venue_state(game):
    try:
        return game['vnue']['address']['state']
    except:
        return ''


def get_home_record(game):
    try:
        return game['teams'][0]['records'][0]['summary']
    except:
        return ''


def get_away_record(game):
    try:
        return game['teams'][1]['records'][0]['summary']
    except:
        return ''


def get_conf_game_ind(game):
    # No longer supported on ESPN scape
    return None


def get_home_score(game):
    try:
        return game['competitors'][0]['score']
    except:
        return 0


def get_away_score(game):
    try:
        return game['competitors'][1]['score']
    except:
        return 0


def get_game_finish(game):
    try:
        return game['status']['type']['completed']
    except:
        return None


def get_game_started(game):
    try:
        return game['status']['period'] > 0
    except:
        return None


def get_game_quarter(game):
    try:
        return game['status']['period']
    except:
        return ''


def get_game_clock(game):
    try:
        return game['status']['displayClock']
    except:
        return ''


def get_home_rank(game):
    try:
        rank = game['teams'][0]['rank']
        if rank <= 25 and rank > 0:
            return rank
        else:
            return None
    except:
        return None


def get_away_rank(game):
    try:
        rank = game['teams'][1]['rank']
        if rank <= 25 and rank > 0:
            return rank
        else:
            return None
    except:
        return None
