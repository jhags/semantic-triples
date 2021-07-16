
from .node import Node


class Triple:
    def __init__(self, subj, predicate, obj):
        self.subj = Node(subj)
        self.predicate = Node(predicate)
        self.obj = Node(obj)
        self.spo = (self.subj.text, self.predicate.text, self.obj.text)

    def __repr__(self):
        return f'({self.subj.phrase} -> {self.predicate.text} -> {self.obj.phrase})'

    def edges(self):
        edges = (self.subj.phrase, self.predicate.phrase, self.obj.phrase)
        edges = [i for i in edges if i is not None]
        return [(edges[i], edges[i+1]) for i in range(len(edges)-1)]
