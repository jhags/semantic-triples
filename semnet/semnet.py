import networkx as nx
from nltk.tokenize import sent_tokenize

from .semantic_triples import get_triples


class Semnet:

    def __init__(self, docs):
        self.docs = docs
        self.triples = self._get_triples()


    def _get_triples(self):
        triples = []
        for item in self.docs:
            t = get_triples(item, subject_propagate=True)
            triples.extend(t)
        return triples


    def nx_graph(self):
        g = nx.DiGraph()
        for trp in self.triples:
            if (trp.subj.text is not None) & (trp.obj.text is not None):
                g.add_edge(trp.subj.text, trp.obj.text, predicate=str(trp.predicate.text))
        return g
