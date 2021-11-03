import networkx as nx
import pandas as pd
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

from .semantic_triples import get_triples


class Semnet:

    def __init__(self, text, spacy_model, tokenize_sentences=True, verbose=True):
        self.text = text
        self._tokenize_sentences = True
        self.sentences = None
        self.triples = None
        self.graph = None

        if tokenize_sentences:
            self.sentences = sent_tokenize(text)
            self.docs = []
            for s in tqdm(self.sentences, disable= not verbose, desc='Converting text to NLP model.'):
                self.docs.append(spacy_model(s))
        else:
            self.sentences = None
            self.docs = spacy_model(docs)


    def get_triples(self):
        triples = []
        for item in self.docs:
            t = get_triples(item, subject_propagate=True)
            triples.extend(t)
        self.triples = triples


    def get_graph(self):
        g = nx.DiGraph()
        for trp in self.triples:
            if (trp.subj.text is not None) & (trp.obj.text is not None):
                g.add_edge(trp.subj.text, trp.obj.text, predicate=str(trp.predicate.text))

        for edge in nx.selfloop_edges(g):
            g.remove_edge(*edge)

        self.graph = g


    def save_graph(self, filepath):
        if self.graph is None:
            raise ValueError(f"Graph not yet processed.")

        nx.write_gexf(self.graph, filepath)
        print(f'Graph saved at: {filepath}')


    def get_graph_data(self):
        return nx.to_pandas_edgelist(self.graph)


    def get_graph_nodes(self):
        return pd.DataFrame(list(self.graph.nodes), columns=['ID'])
