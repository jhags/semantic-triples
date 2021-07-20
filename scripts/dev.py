
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
# from semantic_triples import get_triples
from semnet.semantic_triples import (get_triples, object_propagate_triples,
                                      subject_propagate_triples)

# Get Spacy language packages
nlp = spacy.load('en_core_web_lg')

PRONS = set(open('spacy_prons.txt', 'r').read().split())


def space_fullstops(text_str):
    """ Space fullstops e.g. Bad stop.Good stop. --> Bad stop. Good stop."""
    rx = r"(\.(?=[a-zA-Z]))"
    return re.sub(rx, ". ", text_str)

def remove_numerical_commas(text_str):
    """ Remove commas from numerical numbers e.g. 1,000,000 --> 1000000 """
    rx = r"((?<=\d)\,(?=\d))"
    return re.sub(rx, "", text_str)

def remove_dashes(text_str):
    """ Remove dashes between acronym-styled words where the character preceding the dash is an upper-case letter and the character following the dash is either an upper-case letter or digit, e.g. COVID-19 --> COVID19. one-to-one --> one-to-one."""
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
    trips = get_triples(sent, subject_propagate=True)
    triples.extend(trips)

g = nx.DiGraph()
for trp in triples:
    if (trp.subj.text is not None) & (trp.obj.text is not None):
        g.add_edge(trp.subj.text, trp.obj.text, predicate=str(trp.predicate.text))
nx.write_gexf(g, 'triple_edge_predicates_large.gexf')
