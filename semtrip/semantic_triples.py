
import os
import pandas as pd
import spacy
import string
import networkx as nx
from typing import TypeVar

from .triple import Triple

spacyToken = TypeVar('spacy.tokens.token.Token')

root = os.path.abspath(os.path.join(__file__, "../.."))

# Get Spacy language packages
# nlp = spacy.load('en_core_web_lg')


def get_primary_predicate(subject: spacyToken):
    primary_predicate = subject.head

    if subject.head.pos_ in ['VERB', 'ADP']:
        if primary_predicate.pos_ in ['ADP']:
            if primary_predicate.head.pos_ in ['VERB']:
                primary_predicate = primary_predicate.head
    return primary_predicate


def get_child_dep_dict(token: spacyToken, d=None):
    children = list(token.children)
    children_dep = [child.dep_ for child in children]
    if d is None:
        d = {}
    for dep, child in zip(children_dep, children):
        v = d.get(dep)
        if v is None:
            d[dep] = [child]
        else:
            v.append(child)
    return d


def get_secondary_predicates(primary_predicate: spacyToken):
    dep_dict = get_child_dep_dict(primary_predicate)
    deps = ['conj', 'advcl']
    tokens = []
    for dep in deps:
        token = dep_dict.get(dep, [])
        tokens.extend(token)
    return tokens


def get_objects(predicate: spacyToken):
    d = get_child_dep_dict(predicate)
    deps = ['pobj', 'dobj', 'attr', 'ccomp', 'appos']
    lvl2_dep = ['prep', 'agent', 'relcl', 'acl', 'amod', 'conj']
    tokens = []
    for dep, toks in d.items():
        if dep in deps:
            tokens.extend(toks)

        elif dep in lvl2_dep:
            for tok in toks:
                t = get_objects(tok)
                tokens.extend(t)
    return tokens


# def subject_propagate_triples(doc):
#     subjects = [i.root for i in doc.noun_chunks if i.root.dep_ in ['nsubj', 'nsubjpass']]
#     triples = []
#     for subject in subjects:

#         primary_subject = subject
#         primary_predicate = get_primary_predicate(primary_subject)
#         primary_objects = get_objects(primary_predicate)

#         for obj in primary_objects:
#             triples.append((primary_subject, primary_predicate, obj))

#         # Additional primary objects
#         primary_objects = get_objects(primary_subject)
#         for obj in primary_objects:
#             triples.append((primary_subject, None, obj))

#         # Secondary triples, where the primary subject is the same
#         secondary_predicates = get_secondary_predicates(primary_predicate)
#         for predicate in secondary_predicates:
#             objs = get_objects(predicate)
#             for obj in objs:
#                 triples.append((primary_subject, predicate, obj))

#         # 2nd level objects
#         objs = [obj for (subj, pred, obj) in triples]
#         for obj in objs:
#             lvl2_objs = get_objects(obj)
#             for obj2 in lvl2_objs:
#                 triples.append((obj, None, obj2))

#         # 3rd level objects
#         objs = [obj for (subj, pred, obj) in triples]
#         for obj in objs:
#             lvl3_objs = get_objects(obj)
#             for obj3 in lvl3_objs:
#                 triples.append((obj, None, obj3))

#     triples = list(set(triples))
#     return triples


def subject_propagate_triples(doc):

    subjs = []
    for token in doc:
        if (token.dep_ in ['nsubj', 'nsubjpass']) & (token.pos_ not in ['DET']):
            subjs.append(token)
            # print(token, token.head, token.dep_, token.pos_)

    objs = []
    lvl2_objs = []
    for token in doc:
        if token.dep_ in ['pobj', 'dobj', 'attr', 'ccomp', 'acomp']:
            if token.pos_ not in ['AUX', 'ADJ', 'DET']:
                objs.append(token)
                # print(token, token.head, token.dep_, token.pos_)
        elif token.dep_ in ['conj', 'appos']:
            lvl2_objs.append(token)


    tree = []
    end_nodes = []
    for token in doc:
        children = list(token.children)
        if len(children)>0:
            tree.extend([(token, child) for child in children])
        else:
            end_nodes.append(token)

    tree_graph = nx.DiGraph()
    tree_graph.add_edges_from(tree)
    # nx.draw(tree_graph, with_labels=True, node_size=500)

    paths = []
    for subj in subjs:
        for obj in objs:
            for path in nx.all_simple_paths(tree_graph, source=subj.head, target=obj):
                paths.append([subj] + path)

            for lvl2_obj in lvl2_objs:
                for path in nx.all_simple_paths(tree_graph, source=obj, target=lvl2_obj):
                    # print(obj, '-->', path)
                    paths.append(path)

                for path in nx.all_simple_paths(tree_graph, source=subj, target=lvl2_obj):
                    # print(subj, '-->', lvl2_obj, path)
                    paths.append(path)

    pos_map = {'PROPN': 'NOUN'}

    triples = []
    for path in paths:
        # path = paths[-6]
        path = [t for t in path if (t.pos_ in ['NOUN', 'PROPN', 'VERB'])]
        path_pos = [t.pos_ for t in path]
        path_pos = list(map(pos_map.get, path_pos, path_pos))

        subpaths = [(path[i], path[i+1]) for i in range(len(path)-1)]
        subpaths_pos = [(path_pos[i], path_pos[i+1]) for i in range(len(path_pos)-1)]

        for (sbj, obj), pos in zip(subpaths, subpaths_pos):
            # print(sbj, obj, pos)
            if pos==('NOUN', 'NOUN'):
                triples.append((sbj, None, obj))

        if len(path)>=3:
            # split path into subpaths bounded by nouns.
            # start and end nouns form the subj and obj in Triple
            # the predicate is the last verb between the two nouns
            noun_idxs = [i for (i, x) in enumerate(path) if x.pos_ in ['NOUN', 'PROPN']]
            subpaths = []
            for i1, i2 in [(noun_idxs[i], noun_idxs[i+1]) for i in range(len(noun_idxs)-1)]:
                subpaths.append(path[i1: i2+1])

            for p in subpaths:
                predicate = [t for t in p if t.pos_ in ['VERB']]
                if len(predicate)>0:
                    triples.append((p[0], predicate[-1], p[-1]))

    triples = [(s, p, o) for (s, p, o) in triples if (s.text!=o.text)]
    return list(set(triples))


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


def get_triples(doc, subject_propagate=True, object_propagate=True):
    triples = []

    if subject_propagate:
        subj_triples = subject_propagate_triples(doc)
        triples.extend(subj_triples)

    if object_propagate:
        obj_triples = object_propagate_triples(doc)
        triples.extend(obj_triples)

    triples = list(set(triples))

    t = []
    for trp in triples:
        if len(trp)==3:
            t.append(Triple(*trp))
        elif len(trp)==2:
            t.append(Triple(trp[0], None, trp[1]))
    # print(t)
    return t
