# https://www.analyticsvidhya.com/blog/2019/10/how-to-build-knowledge-graph-text-using-spacy/

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
from tqdm import tqdm
from spacy.matcher import Matcher
import matplotlib.pyplot as plt
import networkx as nx


def get_entities(nlp, sent):
    ent1 = ''
    ent2 = ''

    prv_tok_dep = ''  # dependency tag of previous token in the sentence
    prv_tok_text = ''  # previous token in the sentence

    prefix = ''
    modifier = ''

    for tok in nlp(sent):
        # if token is a punctuation mark then move on to the next token
        if tok.dep_ != 'punct':
            # check: token is a compound word or not
            if tok.dep_ == 'compound':
                prefix = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == 'compound':
                    prefix = prv_tok_text + ' ' + tok.text

            # check: token is a modifier or not
            if tok.dep_.endswith('mod'):
                modifier = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == 'compound':
                    modifier = prv_tok_text + ' ' + tok.text

            if tok.dep_.find('subj') != -1:  # == True:
                ent1 = modifier + ' ' + prefix + ' ' + tok.text
                prefix = ''
                modifier = ''

            if tok.dep_.find('obj') != -1:  # == True:
                ent2 = modifier + ' ' + prefix + ' ' + tok.text

            # update variables
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text

    return [ent1.strip(), ent2.strip()]


def get_relation(nlp, sent):
    doc = nlp(sent)
    # Matcher class object
    matcher = Matcher(nlp.vocab)
    # define the pattern
    pattern = [{'DEP': 'ROOT'},
               {'DEP': 'prep', 'OP': '?'},
               {'DEP': 'agent', 'OP': '?'},
               {'POS': 'ADJ', 'OP': '?'}]
    matcher.add('matching_1', None, pattern)
    matches = matcher(doc)
    k = len(matches) - 1
    span = doc[matches[k][1]:matches[k][2]]
    return span.text


if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    run_start_time = date.today().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(run_start_time, 'vidhya'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    # https://drive.google.com/file/d/1yuEUhkVFIYfMVfpA_crFGfSeJLgbPUxu/view?usp=sharing
    df = pd.read_csv(filepath_or_buffer='./data/wiki_sentences_v2.csv')
    logger.info(df.shape)

    model_name = 'en_core_web_sm'
    model = spacy.load(model_name)

    pairs = [get_entities(model, item) for item in tqdm(df['sentence'])]
    relations = [get_relation(model, item) for item in tqdm(df['sentence'])]
    for pair in pairs:
        logger.info('pair: {}'.format(pair))
    for relation in relations:
        logger.info('relation: {}'.format(relation))

    result_df = pd.DataFrame({'source': [item[0] for item in pairs],
                              'target': [item[1] for item in pairs], 'edge': relations})
    result_df.to_csv(path_or_buf='./vidhya.csv', index=False, header=True, )

    if True:
        graph = nx.from_pandas_edgelist(result_df[result_df['edge'] == 'composed by'], 'source', 'target',
                                        edge_attr=True, create_using=nx.MultiDiGraph())

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(graph, k=0.5)  # k regulates the distance between nodes
        nx.draw(graph, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)
        plt.show()

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
