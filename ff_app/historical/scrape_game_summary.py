import os

import requests
import json
import yaml
from datetime import datetime

from bs4 import BeautifulSoup as bs

import logging

logger = logging.getLogger(__name__)


class ScrapeEspn():
    def __init__(self, year,
                 base_data_dir='~/football/scrape_history/raw_data'):
        self.year = year
        self.data_dir = self.set_data_dir(base_data_dir, year)
        return

    @property
    def summary_url(self):
        return 'http://www.espn.com/college-football/scoreboard/_/group/80/year/{year}/seasontype/2/week/{week}'

    def set_data_dir(self, base_dir, year):
        assert os.path.isdir(os.path.expanduser(base_dir))
        new_dir = os.path.join(os.path.expanduser(base_dir), '{}'.format(year))

        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            logger.info("Setting main data directory to: {}".format(new_dir))
            return new_dir
        else:
            logger.info("Creating main data directory: {}".format(new_dir))
            os.makedirs(new_dir)
            return new_dir


class ScrapeCalendar(ScrapeEspn):
    def set_cal_dir(self, data_dir):
        cal_dir = os.path.join(data_dir, 'calendar')
        if os.path.exists(cal_dir) and os.path.isdir(cal_dir):
            logger.info("Setting calendar directory: {}".format(cal_dir))
            return cal_dir
        else:
            logger.info("Creating calendar directory: {}".format(cal_dir))
            os.makedirs(cal_dir)
            return cal_dir

    def scrape_cal(self):
        cal_url = self.summary_url.format(year=self.year, week=1)
        logger.info("Making GET request for {}".format(cal_url))
        r = requests.get(cal_url)
        soup = bs(r.text, 'html5lib')
        cal = soup.select('script')[13].string.split('\t')[1].strip('= ').split(';')[0]
        return json.loads(cal)['leagues'][0]['calendar'][0]

    def export_cal(self, cal_dict, cal_dir):
        raw_cal_file = os.path.join(cal_dir, 'raw_cal.yaml')
        logger.info("Writing raw calendar data to '{}'".format(raw_cal_file))
        with open(raw_cal_file, 'w') as f:
            yaml.dump(cal_dict, f)

        week_details_file = os.path.join(cal_dir, 'week_details.yaml')
        logger.info("Writing week details data to '{}'".format(week_details_file))
        with open(week_details_file, 'w') as f:
            yaml.dump(self.week_details, f)

        return

    def set_season_attributes(self, data_dict):
        logger.info("Extracting attributes from calendar data")
        self.season_start_date = datetime.strptime(data_dict['startDate'][:10], '%Y-%m-%d')
        self.season_end_date = datetime.strptime(data_dict['endDate'][:10], '%Y-%m-%d')
        self.num_weeks = len(data_dict['entries'])
        self.week_details = {week['value']: {'start_date': week['startDate'][:10],
                                             'end_date': week['endDate'][:10],
                                             'description': week['detail'],
                                             'label': week['label']}
                             for week in data_dict['entries']}
        return

    def run(self):
        logger.info("Running calendar processing for {} season".format(self.year))
        data = self.scrape_cal()
        self.set_season_attributes(data)
        self.export_cal(data, self.set_cal_dir(self.data_dir))
        return data


class ScrapeSummary(ScrapeEspn):
    def set_summary_dir(self, data_dir):
        summary_dir = os.path.join(data_dir, 'summary')
        if os.path.exists(cal_dir) and os.path.isdir(summary_dir):
            logger.info("Setting summary directory: {}".format(summary_dir))
            return summary_dir
        else:
            logger.info("Creating summary directory: {}".format(summary_dir))
            os.makedirs(summary_dir)
            return summary_dir

    def scrape_week_summary(self, week, return_raw_soup=False):
        summary_url = self.summary_url.format(year=self.year, week=week)
        logger.info("Making GET request for {}".format(summary_url))
        r = requests.get(summary_url)
        soup = bs(r.text, 'html5lib')
        if return_raw_soup:
            return soup
        data = soup.select('script')[13].string.split('\t')[1].strip('= ').split(';window')[0]
        return json.loads(data)['events']

    def unpack_links(self, data):
        link_dict = {}
        for game in data:
            link_dict[data['name']]
            link_dict[link['text']] = link['href']
        return link_dict
