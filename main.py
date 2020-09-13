from datetime import date
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

import spacy
import pandas as pd

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

    do_spacy = False
    if do_spacy:
        model = spacy.load('en_core_web_sm')

        document = model("The 22-year-old recently won ATP Challenger tournament.")

        for token in document:
            logger.info('{} ... {}'.format(token.text, token.dep_))

    # https://drive.google.com/file/d/1yuEUhkVFIYfMVfpA_crFGfSeJLgbPUxu/view?usp=sharing
    df = pd.read_csv(filepath_or_buffer='./data/wiki_sentences_v2.csv')
    logger.info(df.shape)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
