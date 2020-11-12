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
from tabula import read_pdf

if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
                                                     'demo_tabula', ))
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

    tables = read_pdf(encoding='utf-8', input_path=input_file, java_options=None, output_format='dataframe',
                      pandas_options=None, multiple_tables=False, user_agent=None, )

    logger.info('table count: {}'.format(len(tables)))
    for index, table_df in enumerate(tables):
        logger.info('{} {}'.format(index, table_df))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
