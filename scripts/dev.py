
import os
import re
import sys

import matplotlib.pyplot as plt
import networkx as nx
import spacy
import wikipedia
from nltk.tokenize import sent_tokenize
from spacy import displacy

root = os.path.abspath(os.path.join(__file__, "../.."))
sys.path.append(root)

# pylint: disable=import-error
import semnet as sn

nlp = spacy.load('en_core_web_lg')
PRONS = set(open('spacy_prons.txt', 'r').read().split())

page = wikipedia.page('COVID-19 pandemic')
text = page.summary
for section in ['Background', 'Cases', 'Deaths']:
    text+=page.section(section)
text = ' '.join(text.split())

sentence = sn.utils.space_sentencestops(text)
sentence = sn.utils.remove_numerical_commas(sentence)
sentence = sn.utils.remove_dashes(sentence)
sentence = sn.utils.sub_common_corrections(sentence)
sentence = ' '.join([i for i in sentence.split() if i not in PRONS])

sentences = sent_tokenize(sentence)
docs = [nlp(s) for s in sentences]

triples = []
for sent in docs:
    trips = sn.get_triples(sent, subject_propagate=True)
    triples.extend(trips)


g = nx.Graph()
for trp in triples:
    if (trp.subj.text is not None) & (trp.obj.text is not None):
        g.add_edge(trp.subj.text, trp.obj.text, predicate=str(trp.predicate.text))

for edge in nx.selfloop_edges(g):
    g.remove_edge(*edge)



# nx.write_gexf(g, 'triple_edge_predicates_large_cluster.gexf')

import itertools

from networkx.algorithms.community import (girvan_newman,
                                           greedy_modularity_communities,
                                           k_clique_communities,
                                           label_propagation_communities)

communities = list(girvan_newman(g))

i = 0
while i<20:
    c = communities[i]
    print(f'Level {i}: nr communities: {len(c)}')
    i+=1
    coms = []
    for i1, c1 in enumerate(c):
        coms.append(len(c1))
        sum(coms)/len(coms)
    print(f"--> Community ave. pop: {str(round(sum(coms)/len(coms), 1))}")

clusters = communities[8]
len(clusters)


node_ids = {}

for idx, cluster in enumerate(clusters):
    # print(idx, cluster)
    for word in cluster:
        node_id = node_ids.get(word)
        if node_id is None:
            node_id = {}
            node_id['girvannewman'] = f"C{idx}"
            node_ids[word] = node_id
        else:
            print(word)

greed_mod_communities = list(greedy_modularity_communities(g))
for idx, cluster in enumerate(greed_mod_communities):
    # print(idx, cluster)
    for word in cluster:
        node_id = node_ids.get(word)
        if node_id is None:
            node_id = {}
            node_id['greedymod'] = f"C{idx}"
            node_ids[word] = node_id
        else:
            node_id['greedymod'] = f"C{idx}"



nx.set_node_attributes(g, node_ids)
g.nodes(data=True)

nx.write_gexf(g, 'triple_edge_predicates_large_cluster.gexf')
