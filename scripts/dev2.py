
from semnet import Semnet
import wikipedia
import spacy

page = wikipedia.page('COVID-19 pandemic')
text = page.summary

# Download spacy model using CLI
# > python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

s = Semnet(text, nlp)
s.get_triples()
s.get_graph()

edges = s.get_graph_data()
nodes = s.get_graph_nodes()

edges.to_csv('test.csv', index=False)
nodes.to_csv('nodes.csv', index=False)
s.save_graph('test.gexf')
