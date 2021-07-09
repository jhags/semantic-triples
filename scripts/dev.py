
import os
import sys
import pytest
import spacy
from spacy import displacy
import networkx as nx
import matplotlib.pyplot as plt

root = os.path.abspath(os.path.join(__file__, "../.."))
sys.path.append(root + r'/scripts')

# pylint: disable=import-error
from semantic_triples import get_triples

# Get Spacy language packages
nlp = spacy.load('en_core_web_sm')


sentence = "London is the capital and largest city of England and the United Kingdom. Standing on the River Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to the North Sea, London has been a major settlement for two millennia. Londinium was founded by the Romans. The City of London, London’s ancient core − an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile − retains boundaries that follow closely its medieval limits. The City of Westminster is also an Inner London borough holding city status. Greater London is governed by the Mayor of London and the London Assembly. London is located in the southeast of England.Westminster is located in London. London is the biggest city in Britain. London has a population of 7,172,036."

sentence = "The City of London, London’s ancient core an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile retains boundaries that follow closely its medieval limits."

sentence = 'Mike said triples can be objects'
doc = nlp(sentence)

get_triples(doc)

edges = []
for trp in triples:
    edges.extend(trp.edges())
edges = list(set(edges))

g = nx.DiGraph()
g.add_edges_from(edges)
g.remove_nodes_from(list(nx.isolates(g)))
pos = nx.spring_layout(g, seed=227)
nx.draw(g, pos, with_labels=True, node_size=500)
plt.margins(x=0.5)
