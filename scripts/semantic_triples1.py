
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import spacy
from spacy import displacy

root = os.path.abspath(os.path.join(__file__, "../.."))

# Get Spacy language packages
nlp = spacy.load('en_core_web_lg')

def add_node(text_str, text_chunk, type):
    text_str = str(text_str)
    text_chunk = str(text_chunk)
    entry = NODES.get(text_str)
    if entry is None:
        NODES[text_str] = {
            "chunk": text_chunk,
            "type": type
        }


def remove_POS(spacy_chunk):
    excl_pos = ['DET']
    return ' '.join([t.text for t in spacy_chunk if t.pos_ not in excl_pos])


def get_children_pos(spacy_token):
    return set([t.pos_ for t in list(spacy_token.children)])


# sentence = "A rare black squirrel has become a regular visitor to a suburban garden"
# sentence = "The man stood beside the large fridge"
# sentence = "the quick brown fox jumps over the lazy dog"
sentence = "London is the capital city of the United Kingdom"
# sentence = "Mike said triples can be objects"

doc = nlp(sentence)

# displacy.render(doc)

NODES = {}
triples = []

subject = None
chunks = []
for chunk in doc.noun_chunks:
    chunks.append(chunk)
    if subject is None:
        subject = chunk.root
        chunk_text = remove_POS(chunk)
        add_node(subject, chunk_text, 'subject')

    else:
        obj = chunk.root
        chunk_text = remove_POS(chunk)
        add_node(obj, chunk_text, 'object')

        predicate = chunk.root.head
        if predicate.pos_ in ['VERB', 'ADP', 'AUX']:
            if predicate.pos_ in ['ADP']:
                if predicate.head.pos_ in ['VERB']:
                    predicate = predicate.head

        if predicate.head.pos_ in ['NOUN']:
            print(f'subject changed {subject} --> {predicate.head}')
            subject = predicate.head

    add_node(predicate, predicate, 'predicate')
    triples.append((subject.text, predicate.text, obj.text))


edges = []
for (s, p, o) in triples:
    edges.extend([(s, p), (p, o)])
edges = list(set(edges))

g = nx.DiGraph()
g.add_nodes_from([(k, v) for k, v in NODES.items()])
g.add_edges_from(edges)
nx.draw(g, with_labels=True, node_size=1000, labels=nx.get_node_attributes(g, 'chunk'))
plt.margins(x=0.2)


# spacy.explain('ADP')

for token in doc:
    print(token.dep_, '\t', token)
