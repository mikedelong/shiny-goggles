# https://medium.com/swlh/python-nlp-tutorial-information-extraction-and-knowledge-graphs-43a2a4c4556c

import datetime
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import stdout
from time import time

from matplotlib.pyplot import axis
from matplotlib.pyplot import figure
from matplotlib.pyplot import show
from matplotlib.pyplot import tight_layout
from networkx import Graph
from networkx import draw
from networkx import spring_layout
from spacy import load
from spacy.lang.en import English


def is_construction_candidate(token):
    return any(subs in token.dep_ for subs in ['compound', 'prep', 'conj', 'mod'])


def process_subject_object_pairs(log, tokens):
    subject = ''
    result_object = ''
    relation = ''
    subject_construction = ''
    object_construction = ''
    for token in tokens:
        log.info('{} > {}'.format(token.text, token.dep_))
        if 'punct' in token.dep_:
            continue
        if any(subs in token.dep_ for subs in ['ROOT', 'adj', 'attr', 'agent', 'amod']):
            relation = relation + ' ' + token.lemma_
        if is_construction_candidate(token):
            if subject_construction:
                subject_construction = subject_construction + ' ' + token.text
            if object_construction:
                object_construction = object_construction + ' ' + token.text
        if 'subj' in token.dep_:
            subject = subject + ' ' + token.text
            subject_construction = subject_construction + ' ' + subject
        if 'obj' in token.dep_:
            result_object = result_object + ' ' + token.text
            result_object = object_construction + ' ' + result_object
            object_construction = ''

    log.info('{}, {}, {}'.format(subject.strip(), relation.strip(), result_object.strip()))
    return subject.strip(), relation.strip(), result_object.strip()


def print_graph(arg):
    graph = Graph()
    for triple in arg:
        for index in range(3):
            graph.add_node(triple[index])
        for index in range(2):
            graph.add_edge(triple[index], triple[index + 1])

    position = spring_layout(graph)
    figure()
    draw(alpha=0.9, edge_color='black', G=graph, labels={node: node for node in graph.nodes()}, linewidths=1,
         node_color='seagreen', node_size=500, pos=position, width=1, )
    axis('off')
    tight_layout()
    show()


if __name__ == '__main__':
    time_start = time()
    LOG_PATH = Path('./logs/')
    LOG_PATH.mkdir(exist_ok=True)
    log_file = str(LOG_PATH / 'log-{}-{}.log'.format(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'), 'borcan'))
    format_ = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
    handlers_ = [FileHandler(log_file, encoding='utf-8', ), StreamHandler(stdout)]
    log_level_ = INFO
    # noinspection PyArgumentList
    basicConfig(datefmt='%m-%d-%Y %H:%M:%S', format=format_, handlers=handlers_, level=log_level_, )
    logger = getLogger(__name__)
    logger.info('started')

    text = 'London is the capital and largest city of England and the United Kingdom. Standing on the River ' \
           'Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to ' \
           'the North Sea, London has been a major settlement for two millennia. ' \
           'Londinium was founded by the Romans. The City of London, ' \
           'London\'s ancient core − an area of just 1.12 square miles (2.9 km2) and colloquially known as ' \
           'the Square Mile − retains boundaries that follow closely its medieval limits.' \
           'The City of Westminster is also an Inner London borough holding city status. ' \
           'Greater London is governed by the Mayor of London and the London Assembly.' \
           'London is located in the southeast of England.' \
           'Westminster is located in London.' \
           'London is the biggest city in Britain. London has a population of 7,172,036.'

    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    document = nlp(text=text)
    sentences = [sentence.string.strip() for sentence in document.sents]

    model = load('en_core_web_sm')

    triples = []
    for sentence in sentences:
        logger.info(sentence)
        triples.append(process_subject_object_pairs(logger, model(sentence)))

    print_graph(triples)
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
