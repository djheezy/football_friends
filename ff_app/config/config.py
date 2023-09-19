"""
"""

import yaml
import inspect
import os
import ff_app


BASE_PATH = os.path.dirname(ff_app.__file__)


def load_config(config_path=None):
    config_path = config_path \
        or os.path.join(BASE_PATH, 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

CONFIG = load_config()


def load_team_lookup(lookup_path=None):
    lookup_path = lookup_path \
        or os.path.join(BASE_PATH, 'config', 'team_lookup.yaml')
    with open(lookup_path, 'r') as f:
        lookup = yaml.safe_load(f)
    return lookup

TEAM_LOOKUP = load_team_lookup()
