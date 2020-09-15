# https://medium.com/swlh/python-nlp-tutorial-information-extraction-and-knowledge-graphs-43a2a4c4556c
import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt


def get_sentences(text):
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    document = nlp(text)
    return [sent.string.strip() for sent in document.sents]


def print_token(token):
    print(token.text, "->", token.dep_)


def append_chunk(original, chunk):
    return original + ' ' + chunk


def is_relation_candidate(token):
    deps = ["ROOT", "adj", "attr", "agent", "amod"]
    return any(subs in token.dep_ for subs in deps)


def is_construction_candidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)


def process_subject_object_pairs(tokens):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        print_token(token)
        if "punct" in token.dep_:
            continue
        if is_relation_candidate(token):
            relation = append_chunk(relation, token.lemma_)
        if is_construction_candidate(token):
            if subjectConstruction:
                subjectConstruction = append_chunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = append_chunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = append_chunk(subject, token.text)
            subject = append_chunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = append_chunk(object, token.text)
            object = append_chunk(objectConstruction, object)
            objectConstruction = ''

    print(subject.strip(), ",", relation.strip(), ",", object.strip())
    return subject.strip(), relation.strip(), object.strip()


def process_sentence(sentence):
    tokens = nlp_model(sentence)
    return process_subject_object_pairs(tokens)


def print_graph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='seagreen', alpha=0.9,
            labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.show()


if __name__ == "__main__":

    text = "London is the capital and largest city of England and the United Kingdom. Standing on the River " \
           "Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to " \
           "the North Sea, London has been a major settlement for two millennia. " \
           "Londinium was founded by the Romans. The City of London, " \
           "London's ancient core − an area of just 1.12 square miles (2.9 km2) and colloquially known as " \
           "the Square Mile − retains boundaries that follow closely its medieval limits." \
           "The City of Westminster is also an Inner London borough holding city status. " \
           "Greater London is governed by the Mayor of London and the London Assembly." \
           "London is located in the southeast of England." \
           "Westminster is located in London." \
           "London is the biggest city in Britain. London has a population of 7,172,036."

    sentences = get_sentences(text)
    nlp_model = spacy.load('en_core_web_sm')

    triples = []
    print(text)
    for sentence in sentences:
        triples.append(process_sentence(sentence))

    print_graph(triples)
