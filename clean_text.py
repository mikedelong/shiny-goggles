import datetime
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer


def remove_citation(arg):
    for index, index_item in enumerate(arg[:-2]):
        if all([index_item == '[', arg[index + 1].strip().isnumeric(), arg[index + 2] == ']']):
            result = arg[:index] + arg[index + 3:]
            return result if result is not None else list()
    return arg


if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    run_start_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(run_start_time, 'clean_text'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    detokenizer = TreebankWordDetokenizer()

    input_encoding = 'utf-8'
    input_file = './constitution.txt'
    with open(encoding=input_encoding, file=input_file, mode='r') as input_fp:
        text = input_fp.read()

    text = text.replace('\n', ' ')
    sentences = sent_tokenize(text=text)
    clean = list()
    logger.info(len(sentences))
    sentences = [item for item in sentences if item is not None]
    for sentence in sentences:
        sentence = sentence.replace('—', ' - ').replace('–', ' - ').replace('"', ' ')
        words = word_tokenize(sentence)
        length = len(words)
        original_length = length
        updated = remove_citation(words)
        length_updated = len(updated) if updated is not None else 0
        while length > length_updated:
            length = length_updated
            updated = remove_citation(words)
            length_updated = len(updated)
        if length < original_length:
            sentence = detokenizer.detokenize(updated)
        clean.append(sentence)
    output_encoding = 'ascii'
    with open(encoding=output_encoding, file='./clean_constitution.txt', mode='w',) as out_fp:
        for item in clean:
            out_fp.write('{}\n'.format(item))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
