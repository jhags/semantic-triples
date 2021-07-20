
import os
import spacy
import networkx as nx
from typing import TypeVar

from .triple import Triple

spacyToken = TypeVar('spacy.tokens.token.Token')
spacySpan = TypeVar('spacy.tokens.span.Span')


def object_propagate_triples(doc):

    objs = []
    for token in doc:
        if token.dep_ in ['pobj', 'dobj', 'attr', 'ccomp', 'appos', 'acomp']:
            if token.pos_ not in ['AUX', 'ADJ']:
                objs.append(token)
                # print(token, token.head, token.dep_, token.pos_)

    trees = []
    for obj in objs:
        tree = [obj]
        get_next = True
        while get_next:
            token = tree[-1]
            next_head = token.head
            if token!=next_head:
                tree.append(next_head)
            else:
                get_next = False

        for child in token.children:
            # print(child)
            if child.dep_ in ['nsubj', 'nsubjpass']:
                tree.append(child)
        trees.append(list(reversed(tree)))
    # print(trees)

    triples = []
    for tree in trees:
        subjs, preds, objs = [], [], []
        # print(tree)
        for token in tree:
            dep = token.dep_
            pos = token.pos_
            # print(token, dep, pos)
            if dep in ['nsubj', 'nsubjpass']:
                subjs.append(token)
            elif (dep in ['ROOT', 'advcl', 'conj', 'pcomp']) & (pos in ['VERB', 'NOUN']):
                preds.append(token)
            elif (dep in ['pobj', 'dobj', 'attr', 'ccomp', 'appos', 'acomp', 'amod']) & (pos not in ['AUX', 'ADJ']):
                objs.append(token)

        subj = None if len(subjs)==0 else subjs[0]
        pred = None if len(preds)==0 else preds[0]
        obj = None if len(objs)==0 else objs[0]

        triples.append(((subj, pred, obj)))

        if len(objs)>1:
            lvl2 = [(objs[i], objs[i+1]) for i in range(len(objs)-1)]
            triples.extend(lvl2)

    triples = list(set(triples))
    # print(triples)
    return triples
