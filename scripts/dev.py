
import os
import re
import string
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
# from semantic_triples import get_triples
from semtrip.semantic_triples import (get_triples, object_propagate_triples,
                                      subject_propagate_triples)
from semtrip.triple import Triple

# Get Spacy language packages
nlp = spacy.load('en_core_web_sm')

PRONS = set(open('spacy_prons.txt', 'r').read().split())


def space_fullstops(text_str):
    rx = r"(\.(?=[a-zA-Z]))"
    return re.sub(rx, ". ", text_str)

def remove_numerical_commas(text_str):
    rx = r"((?<=\d)\,(?=\d))"
    return re.sub(rx, "", text_str)

def remove_dashes(text_str):
    rx = r"((?<=[A-Z])\-(?=[A-Z|\d]))"
    return re.sub(rx, "", text_str)

def sub_common_corrections(text_str):
    corrections = {
        "percent": "%",
        "per cent": "%"
    }
    for k, v in corrections.items():
        rx = fr"((?:{k}| {k}))"
        text_str = re.sub(rx, v, text_str)
    return text_str


page = wikipedia.page('COVID-19 pandemic')

text = page.summary
for section in ['Background', 'Cases', 'Deaths']:
    text+=page.section(section)
text = ' '.join(text.split())

sentence = space_fullstops(text)
sentence = remove_numerical_commas(sentence)
sentence = remove_dashes(sentence)
sentence = sub_common_corrections(sentence)
sentence = ' '.join([i for i in sentence.split() if i not in PRONS])

sentences = sent_tokenize(sentence)

docs = [nlp(s) for s in sentences]

triples = []
for sent in docs:
    # print(sent)
    # displacy.render(sent)
    trips = get_triples(sent, subject_propagate=True, object_propagate=False)
    triples.extend(trips)

g = nx.DiGraph()
for trp in triples:
    if (trp.subj.phrase is not None) & (trp.obj.phrase is not None):
        g.add_edge(trp.subj.phrase, trp.obj.phrase, predicate=str(trp.predicate.phrase))
nx.write_gexf(g, 'triple_edge_predicates_large.gexf')


# edges = []
# for trp in triples:
#     edges.extend(trp.edges())
# edges = list(set(edges))

# g = nx.DiGraph()
# g.add_edges_from(edges)
# g.remove_nodes_from(list(nx.isolates(g)))
# nx.write_gexf(g, 'triple_with_predicate_nodes.gexf')


# pos = nx.spring_layout(g)
# edge_labels = nx.get_edge_attributes(g,'predicate')
# nx.draw_networkx_edge_labels(g, pos, edge_labels)
# nx.draw(g, pos, with_labels=True, node_size=500)
# plt.margins(x=0.5)

# sentence = "London is the capital and largest city of England and the United Kingdom. Standing on the River Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to the North Sea, London has been a major settlement for two millennia. Londinium was founded by the Romans. The City of London, London’s ancient core an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile retains boundaries that follow closely its medieval limits. The City of Westminster is also an Inner London borough holding city status. Greater London is governed by the Mayor of London and the London Assembly. London is located in the southeast of England.Westminster is located in London. London is the biggest city in Britain. London has a population of 7,172,036."

# text = "The City of London, London’s ancient core an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile retains boundaries that follow closely its medieval limits."

# text = "The World Health Organization declared the virus a Public Health Emergency of International Concern on 30 January 2020, and later a pandemic on 11 March 2020. "
# text = "Recommended preventive measures include social distancing, wearing face masks in public, ventilation and air-filtering, hand washing, covering one's mouth when sneezing or coughing, disinfecting surfaces, and monitoring and self-isolation for people exposed or symptomatic."
# text = "The ongoing global pandemic of coronavirus disease 2019 (COVID-19) is caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)."
# sentence = "The severity of COVID-19 symptoms is highly variable, ranging from unnoticeable to life-threatening."
# sentence = "COVID-19 transmits when people breathe in air contaminated by droplets and small airborne particles."
# text = "The risk of breathing these in is highest when people are in close proximity, but they can be inhaled over longer distances, particularly indoors."

# text = "The current scientific consensus is that the virus is most likely of zoonotic origin, from bats or another closely related mammal."
