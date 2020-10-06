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


def make_graph(arg):
    result = Graph()
    for triple in arg:
        # todo unhack this
        if all([len(triple[index]) > 0 for index in range(3)]):
            for index in range(3):
                result.add_node(triple[index])
            for index in range(2):
                if (triple[index], triple[index + 1]) in result.edges:
                    result[triple[index]][triple[index + 1]]['weight'] = result[triple[index]][triple[index + 1]][
                                                                             'weight'] + 1
                else:
                    result.add_edge(triple[index], triple[index + 1], weight=1)
    return result


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


def reduce(arg_graph, threshold):
    edges = [edge for edge in arg_graph.edges(data=True) if edge[2]['weight'] > threshold]
    result = Graph()
    for edge in edges:
        result.add_node(node_for_adding=edge[0])
        result.add_node(node_for_adding=edge[1])
        result.add_edge(u_of_edge=edge[0], v_of_edge=edge[1], weight=edge[2]['weight'])
    return result


def show_graph(arg_graph, graph_package, cytoscape_layout, cytoscape_host, cytoscape_port, ):
    position = spring_layout(arg_graph)
    if graph_package == 'networkx':
        figure()
        draw(alpha=0.9, edge_color='black', G=arg_graph, labels={node: node for node in arg_graph.nodes()},
             linewidths=1, node_color='seagreen', node_size=500, pos=position, width=1, )
        axis('off')
        tight_layout()
        show()
    elif graph_technology == 'cytoscape':
        cytoscape_graph = cytoscape_data(arg_graph)
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
    logger.info('settings: {}'.format(pformat(settings, ), ), )
    host = settings['host']
    input_file = settings['text']
    input_encoding = settings['text_encoding']
    pipeline_name = settings['pipeline']
    port = settings['port']
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

    triples = [triple for triple in triples if all([len(triple[index]) > 0 for index in range(3)])]
    do_reduced = False
    graph = make_graph(triples)
    to_show = graph if not do_reduced else reduce(arg_graph=graph, threshold=1, )

    show_graph(arg_graph=to_show, cytoscape_layout=layout, cytoscape_host=host, cytoscape_port=port,
               graph_package=graph_technology, )

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
