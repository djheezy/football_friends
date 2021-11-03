from setuptools import setup, find_packages

setup(
    name="Football Friends",
    version="2021.0.0",
    packages=find_packages(),
    author="Hoke Hill",
    description="Scraper and Publisher of College Football game data",
    install_requires=['pandas',
                      'numpy',
                      'bs4',
                      'pytz',
                      'pyyaml',
                      'google-api-core',
                      'google-api-python-client',
                      'google-auth',
                      'google-auth-httplib2',
                      'google-auth-oauthlib',
                      'googleapis-common-protos'
                      ]

)
