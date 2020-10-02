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
from scipy.sparse import coo_matrix
from numpy import where
from numpy import intersect1d


def half_max(arg):
    row_value = arg.row
    col_value = arg.col
    value = arg.data
    shape = arg.shape
    row_result = list()
    col_result = list()
    value_result = list()
    stencil_values = list()
    for i in range(shape[0] // 2):
        for j in range(shape[1] // 2):
            for ki in range(i, i + 2):
                for kj in range(j, j + 2):
                    result_i = where(row_value == ki)
                    result_j = where(col_value == kj)
                    common = intersect1d(result_i, result_j)
                    for item in common:
                        stencil_values.append(value[item])
            if len(stencil_values) != 0:
                row_result.append(i)
                col_result.append(j)
                value_result.append(max(stencil_values))
    return coo_matrix((value_result, (row_result, col_result)), shape=(shape[0] // 2, shape[1] // 2))


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
    do_example = True
    if do_example:
        half = half_max(data)
        logger.info(half.nnz)
    else:
        logger.info(data.nnz)
        logger.info(data.row)
        logger.info(data.col)
        logger.info(data.data)
        n_samples = 50
        result = resample(data, n_samples=n_samples, random_state=random_state)

        logger.info(result.nnz)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
