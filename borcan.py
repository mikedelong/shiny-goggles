# https://medium.com/swlh/python-nlp-tutorial-information-extraction-and-knowledge-graphs-43a2a4c4556c

import datetime
from json import load as load_json
from logging import FileHandler
from logging import INFO
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from pprint import pformat
from sys import stdout
from time import time

from dash import Dash
from dash_cytoscape import Cytoscape
from dash_html_components import Div
from matplotlib.pyplot import axis
from matplotlib.pyplot import figure
from matplotlib.pyplot import show
from matplotlib.pyplot import tight_layout
from networkx import Graph
from networkx import draw
from networkx import spring_layout
from networkx.readwrite import cytoscape_data
from spacy import load as load_spacy
from spacy.lang.en import English


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
        if any(subs in token.dep_ for subs in ['compound', 'prep', 'conj', 'mod']):
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


def show_graph(arg, graph_package, cytoscape_layout, cytoscape_host, cytoscape_port, ):
    graph = Graph()
    for triple in arg:
        for index in range(3):
            graph.add_node(triple[index])
        for index in range(2):
            graph.add_edge(triple[index], triple[index + 1])

    position = spring_layout(graph)
    if graph_package == 'networkx':
        figure()
        draw(alpha=0.9, edge_color='black', G=graph, labels={node: node for node in graph.nodes()}, linewidths=1,
             node_color='seagreen', node_size=500, pos=position, width=1, )
        axis('off')
        tight_layout()
        show()
    elif graph_technology == 'cytoscape':
        cytoscape_graph = cytoscape_data(graph)
        cytoscape_nodes = [{'data': {'id': item['data']['id'], 'label': item['data']['name']}} for item in
                           cytoscape_graph['elements']['nodes']]

        app = Dash(__name__)
        app.layout = Div([
            Cytoscape(
                id='cytoscape',
                elements=cytoscape_nodes + cytoscape_graph['elements']['edges'],
                style={'width': '100%', 'height': '700px'},
                layout={'name': cytoscape_layout}
            )
        ])
        app.run_server(debug=True, host=cytoscape_host, port=cytoscape_port, )
    else:
        raise NotImplemented('not supported: {}'.format(graph_technology))


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

    with open(encoding='ascii', file='./borcan_settings.json', mode='r', ) as settings_fp:
        settings = load_json(fp=settings_fp)
    logger.info('settings: {}'.format(pformat(settings)))
    input_file = settings['text']
    input_encoding = settings['text_encoding']
    pipeline_name = settings['pipeline']
    spacy_model = settings['spacy_model']
    graph_technologies = ['cytoscape', 'networkx', ]
    graph_technology = graph_technologies[0]
    layouts = settings['layouts']
    layout_selection = settings['layout']
    layout = layouts[layout_selection]

    with open(encoding=input_encoding, file=input_file, mode='r', ) as input_fp:
        text = input_fp.readlines()
    text = ' '.join([item.strip() for item in text])

    nlp = English()
    nlp.add_pipe(nlp.create_pipe(pipeline_name))
    document = nlp(text=text)
    sentences = [sentence.string.strip() for sentence in document.sents]

    model = load_spacy(spacy_model)

    triples = []
    for sentence in sentences:
        logger.info(sentence)
        triples.append(process_subject_object_pairs(logger, model(sentence)))

    show_graph(arg=triples, graph_package=graph_technology, cytoscape_layout=layout, cytoscape_host='localhost',
               cytoscape_port=8052, )
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
