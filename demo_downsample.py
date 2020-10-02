import datetime
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time
from scipy.sparse import random
from sklearn.utils import resample

if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
                                                     'demo_downsample'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    m = 500
    n = 500
    density = 0.01
    storage_format = 'coo'
    random_state = 1
    data_rvs = None
    data = random(m=m, n=n, format=storage_format, random_state=random_state, data_rvs=data_rvs)
    logger.info(data.nnz)

    n_samples = 50
    result = resample(data, n_samples=n_samples, random_state=random_state)

    logger.info(result.nnz)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
