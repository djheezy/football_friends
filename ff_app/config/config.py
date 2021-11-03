"""
"""

import yaml
import inspect
import os
import ff_app

def load_config(config_path=None):
    config_path = config_path \
        or os.path.join(os.path.dirname(ff_app.__file__),
                        'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

CONFIG = load_config()
