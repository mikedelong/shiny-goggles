import datetime
from json import load
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

from camelot import read_pdf

if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
                                                     'demo_camelot', ))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    with open(encoding='ascii', file='./settings.json', mode='r', ) as settings_fp:
        settings = load(fp=settings_fp, )
    logger.info(settings)
    input_file = settings['input_file']

    tables = read_pdf(filepath=input_file, flavor='lattice', pages='1-end', password=None, suppress_stdout=False, )
    logger.info(len(tables))
    for index, table in enumerate(tables):
        logger.info('{} {}'.format(index, table.df.shape))
        logger.info('\n{}'.format(table.df))
        logger.info(table.parsing_report)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
