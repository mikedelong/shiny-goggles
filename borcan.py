# https://medium.com/swlh/python-nlp-tutorial-information-extraction-and-knowledge-graphs-43a2a4c4556c
import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt


def get_sentences(arg):
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    document = nlp(arg)
    return [sent.string.strip() for sent in document.sents]


def print_token(token):
    print(token.text, '->', token.dep_)


def is_relation_candidate(token):
    return any(subs in token.dep_ for subs in ['ROOT', 'adj', 'attr', 'agent', 'amod'])


def is_construction_candidate(token):
    return any(subs in token.dep_ for subs in ['compound', 'prep', 'conj', 'mod'])


def process_subject_object_pairs(tokens):
    subject = ''
    result_object = ''
    relation = ''
    subject_construction = ''
    object_construction = ''
    for token in tokens:
        print_token(token)
        if 'punct' in token.dep_:
            continue
        if is_relation_candidate(token):
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

    print(subject.strip(), ',', relation.strip(), ',', result_object.strip())
    return subject.strip(), relation.strip(), result_object.strip()


def process_sentence(arg):
    return process_subject_object_pairs(nlp_model(arg))


def print_graph(arg):
    graph = nx.Graph()
    for triple in arg:
        for index in range(3):
            graph.add_node(triple[index])
        for index in range(2):
            graph.add_edge(triple[index], triple[index + 1])

    pos = nx.spring_layout(graph)
    plt.figure()
    nx.draw(alpha=0.9, edge_color='black', G=graph, labels={node: node for node in graph.nodes()}, linewidths=1,
            node_color='seagreen', node_size=500, pos=pos, width=1, )
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

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

    sentences = get_sentences(text)
    nlp_model = spacy.load('en_core_web_sm')

    triples = []
    print(text)
    for sentence in sentences:
        triples.append(process_sentence(sentence))

    print_graph(triples)
