import os

import requests
import json
import yaml
from datetime import datetime
import re

from bs4 import BeautifulSoup as bs

import logging

logger = logging.getLogger(__name__)


class ScrapeGamePlays():
    """
    Object containing the details and play-by-play of a single game

    Parameters
    ----------
    game_id : str
        ESPN-specific unique ID for a single game
    """
    def __init__(self, game_id):
        self.game_id = game_id
        self.game_url = self.set_game_url(game_id)
        self.request_data = self.request_data()

    def set_game_url(self, game_id):
        return 'http://www.espn.com/college-football/playbyplay?gameId={game_id}'.format(game_id=game_id)

    @property
    def request(self):
        r = requests.get(self.game_url)
        return r

    def request_data(self, request_instance=None):
        request = request_instance or self.request
        soup = bs(request.text, "html5lib")
        return soup

    @property
    def number_of_drives(self):
        soup = self.request_data
        game_tag = re.compile('(gp-playbyplay-{}).*'.format(self.game_id))
        return len(soup.find_all("a", attrs={'href': game_tag}))

    def get_drive_ids(self):
        return [x.find("a")['aria-controls'] for x in self.request_data.find_all("div", class_='accordion-header')]

    def get_raw_drive_summary(self, drive_id):
        return self.request_data.find("a", attrs={'href': drive_id})

    def drive_summary(self, drive_id):
        raw = self.get_raw_drive_summary(drive_id)
        s_dict = {}
        if raw:
            s_dict['home_score'] = raw.find("span", class_="home").find("span", class_="team-score").text
            s_dict['away_score'] = raw.find("span", class_="away").find("span", class_="team-score").text
            summary_str = raw.find("span", class_="drive-details").text
            s_dict['drive_team'] = summary_str.split(' drive')[0]
            s_dict['num_plays'] = int(summary_str.split('drive: ')[1].split(' play')[0])
            if 'plays' in summary_str:
                s_dict['num_yards'] = int(summary_str.split('plays ')[1].split(' yard')[0])
            else:
                s_dict['num_yards'] = int(summary_str.split('play ')[1].split(' yard')[0])
            if 'yards' in summary_str:
                s_dict['drive_time'] = summary_str.split('yards, ')[1].split()[0]
            else:
                s_dict['drive_time'] = summary_str.split('yard, ')[1].split()[0]
            s_dict['drive_result'] = summary_str.split(s_dict['drive_team'])[2].split(',')[0].strip()

        return s_dict

    def get_raw_drive_plays(self, drive_id):
        return self.request_data.find("div", id=drive_id).find("ul", attrs={'class': 'drive-list'})

    def drive_plays(self, drive_id):
        raw = self.get_raw_drive_plays(drive_id)
        play_dict = {}
        for i, play in enumerate(raw.find_all("li", attrs={'class': ''})):
            play_dict[i] = {
                'down_and_dist': play.find("h3").text,
                'play_result': play.find("span").text.strip()
            }
        return play_dict

    def drive(self, drive_id):
        drive = {'summary': self.drive_summary(drive_id),
                 'plays': self.drive_plays(drive_id)}
        return drive

    def all_drives(self):
        all_drives_dict = {}
        for drive in self.get_drive_ids():
            all_drives_dict[drive] = self.drive(drive)
        return all_drives_dict
