
import os
import sys
import pytest
import spacy
from spacy import displacy
import networkx as nx
import matplotlib.pyplot as plt
import string

import wikipedia

root = os.path.abspath(os.path.join(__file__, "../.."))
sys.path.append(root + r'/scripts')

# pylint: disable=import-error
from semantic_triples import get_triples, Node

# Get Spacy language packages
nlp = spacy.load('en_core_web_sm')

PRONS = set(open('spacy_prons.txt', 'r').read().split())

def remove_punctuation(text_str):
    chars = '()−' #string.punctuation
    for char in chars:
        text_str = text_str.replace(char, ' ')

    chars = '-' #string.punctuation
    for char in chars:
        text_str = text_str.replace(char, '')

    return ' '.join(text_str.split())

# page = wikipedia.page('COVID-19 pandemic')
# page.title
# sentence = page.summary

# sentence = "London is the capital and largest city of England and the United Kingdom. Standing on the River Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to the North Sea, London has been a major settlement for two millennia. Londinium was founded by the Romans. The City of London, London’s ancient core an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile retains boundaries that follow closely its medieval limits. The City of Westminster is also an Inner London borough holding city status. Greater London is governed by the Mayor of London and the London Assembly. London is located in the southeast of England.Westminster is located in London. London is the biggest city in Britain. London has a population of 7,172,036."

sentence = "The ongoing global pandemic of coronavirus disease 2019 (COVID-19) is caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2). The virus was first identified in December 2019 in Wuhan, China. The World Health Organization declared a Public Health Emergency of International Concern on 30 January 2020, and later declared a pandemic on 11 March 2020. As of 9 July 2021, more than 185 million cases have been confirmed, with more than 4.01 million confirmed deaths attributed to COVID-19, making it one of the deadliest pandemics in history.The severity of COVID-19 symptoms is highly variable, ranging from unnoticeable to life-threatening. Severe illness is more likely in elderly COVID-19 patients, as well as those who have certain underlying medical conditions. COVID-19 transmits when people breathe in air contaminated by droplets and small airborne particles. The risk of breathing these in is highest when people are in close proximity, but they can be inhaled over longer distances, particularly indoors. Transmission can also occur if splashed or sprayed with contaminated fluids, in the eyes, nose or mouth, and, rarely, via contaminated surfaces. People remain contagious for up to 20 days, and can spread the virus even if they do not develop any symptoms.Recommended preventive measures include social distancing, wearing face masks in public, ventilation and air-filtering, hand washing, covering one's mouth when sneezing or coughing, disinfecting surfaces, and monitoring and self-isolation for people exposed or symptomatic. Several vaccines have been developed and widely distributed in most developed countries since December 2020. Current treatments focus on addressing symptoms, but work is underway to develop medications that inhibit the virus. Authorities worldwide have responded by implementing travel restrictions, lockdowns and quarantines, workplace hazard controls, and business closures. Numerous jurisdictions have also worked to increase testing capacity and trace contacts of the infected. The pandemic has resulted in severe global, social and economic disruption, including the largest global recession since the Great Depression of the 1930s. It has led to widespread supply shortages exacerbated by panic buying, agricultural disruption, and food shortages. However, it has also caused temporary decreases in emissions of pollutants and greenhouse gases. Numerous educational institutions and public areas have been partially or fully closed, and many events have been cancelled or postponed. Misinformation has circulated through social media and mass media, and political tensions have been exacerbated. The pandemic has raised issues of racial and geographic discrimination, health equity, wealth inequality and the balance between public health imperatives and individual rights."
# sentence = "The City of London, London’s ancient core an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile retains boundaries that follow closely its medieval limits."


# sentence = "The World Health Organization declared a Public Health Emergency of International Concern on 30 January 2020, and later declared a pandemic on 11 March 2020."
# sentence = "Recommended preventive measures include social distancing, wearing face masks in public, ventilation and air-filtering, hand washing, covering one's mouth when sneezing or coughing, disinfecting surfaces, and monitoring and self-isolation for people exposed or symptomatic."
# sentence = "The ongoing global pandemic of coronavirus disease 2019 (COVID-19) is caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)."

sentence = ' '.join([i for i in sentence.split() if i not in PRONS])
sentence = remove_punctuation(sentence)

doc = nlp(sentence)

# displacy.render(doc)
triples = get_triples(doc)

edges = []
for trp in triples:
    edges.extend(trp.edges())
edges = list(set(edges))

g = nx.DiGraph()
g.add_edges_from(edges)
g.remove_nodes_from(list(nx.isolates(g)))
# pos = nx.spring_layout(g, seed=227)
# nx.draw(g, pos, with_labels=True, node_size=500)
# plt.margins(x=0.5)

nx.write_gexf(g, 'triple.gexf')


