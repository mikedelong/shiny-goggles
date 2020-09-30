# https://stackoverflow.com/questions/61917404/scatter-plot-for-scipy-sparse-csr-csr-matrix
import datetime
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

from matplotlib.pyplot import colorbar
from matplotlib.pyplot import scatter
from matplotlib.pyplot import savefig
from numpy import array
from numpy.random import randint
from numpy.random import seed
from numpy.random import uniform
from scipy.sparse import csr_matrix

if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
                                                     'demo_sparse_scatter'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    seed(seed=1, )
    N = 15000
    points_count = 1000
    matrix = csr_matrix((uniform(0, 0.2, points_count), (randint(0, N, points_count), randint(0, N, points_count))),
                        shape=(N, N))

    matrix_dict = matrix.todok()
    xy = array(list(matrix_dict.keys()))
    values = array(list(matrix_dict.values()))

    # create a scatter plot
    scatter(xy[:, 0], xy[:, 1], s=5, c=values, cmap='inferno')
    colorbar()
    output_file = './demo_sparse_scatter.png'
    logger.info('saving scatter plot to ')
    savefig(output_file)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
