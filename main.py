from datetime import date
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

from entity_pair import entity_pair
from from_wiki import wiki_scrape

if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    run_start_time = date.today().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(run_start_time, 'main'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    wiki_data = wiki_scrape('Financial crisis of 2007–08')

    pairs = entity_pair(wiki_data.loc[0, 'text'])

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
