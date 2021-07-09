
import os
import pandas as pd
import spacy
from spacy import displacy
import networkx as nx
import matplotlib.pyplot as plt


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


sentence = "A rare black squirrel has become a regular visitor to a suburban garden"
sentence = "The man stood beside the large fridge"
sentence = "the quick brown fox jumps over the lazy dog"
sentence = "London is the capital city of the United Kingdom"
sentence = "Mike said triples can be objects"

doc = nlp(sentence)

displacy.render(doc)

# DEP_SUBJECT = []

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

def find_child_objects(spacy_token):
    children = list(spacy_token.children)
    children_dep = [child.dep_ for child in children]
    children_dict = dict(zip(children_dep, children))

    deps = ['pobj', 'attr', 'ccomp', 'prep']
    for dep in deps:
        token = children_dict.get(dep)
        if token is not None:
            if dep=='prep':
                return find_child_objects(token)
            return token


subjects = []
for chunk in doc.noun_chunks:
    if chunk.root.dep_ in ['nsubj']:
        subjects.append((chunk.root, chunk))
# subject, chunk = obj, obj
# subject.head
triples = []
for (subject, chunk) in subjects:
    predicate, obj = None, None
    predicate = chunk.root.head
    if predicate.pos_ in ['VERB', 'ADP', 'AUX']:
        if predicate.pos_ in ['ADP']:
            if predicate.head.pos_ in ['VERB']:
                predicate = predicate.head

    obj = find_child_objects(predicate)

    triples.append((subject, predicate, obj))

# for (root, chunk) in subjects:
#     print(root, root.head, list(root.head.children))

########################
triples = []
for chunk in doc.noun_chunks:
    subj = chunk.root
    pred = chunk.root.head
    for child in list(chunk.root.head.children):
        if child.pos_ in ['NOUN']:
            obj = child
            break
        elif child.pos_ in ['AUX']:
            obj = child
            break

    triples.append((subj, pred, obj))




edges = []
for (s, p, o) in triples:
    edges.extend([(s, p), (p, o)])
edges = list(set(edges))

g = nx.DiGraph()
g.add_nodes_from([(k, v) for k, v in NODES.items()])
g.add_edges_from(edges)
nx.draw(g, with_labels=True, node_size=1000, labels=nx.get_node_attributes(g, 'chunk'))
plt.margins(x=0.2)


spacy.explain('mod')

for token in doc:
    print(token.dep_, '\t', token)