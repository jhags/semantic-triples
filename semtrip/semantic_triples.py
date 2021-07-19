
import os
import spacy
import networkx as nx
from typing import TypeVar

from .triple import Triple

spacyToken = TypeVar('spacy.tokens.token.Token')
spacySpan = TypeVar('spacy.tokens.span.Span')


def get_chunk(token):
    chunks = [c for c in token.doc.noun_chunks if token in c]
    if len(chunks)==0: return token
    return chunks[0]

def get_max_chunk(token):
    if token is None:
        return None

    ent_idxs = [(i, (i.start_char, i.end_char)) for i in token.doc.ents]
    chunk_idxs = [(i, (i.start_char, i.end_char)) for i in token.doc.noun_chunks]

    for chunk_idx in chunk_idxs:
        for ent_idx in ent_idxs:
            if (token in ent_idx[0]) or (token in chunk_idx[0]):
                a = set(range(*ent_idx[1]))
                b = set(range(*chunk_idx[1]))
                if len(a.intersection(b))>0:
                    min_idx = min(min(ent_idx[1]), min(chunk_idx[1]))
                    max_idx = max(max(ent_idx[1]), max(chunk_idx[1]))
                    return token.doc.char_span(min_idx, max_idx)

    return get_chunk(token)


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
        path = [t for t in path if (t.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADP', 'AUX'])]
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

            primary_predicates = [] #verbs
            secondary_predicates = [] # ADPs, AUXs etc.
            for p in subpaths:
                primary_predicates = list(reversed([t for t in p if t.pos_ in ['VERB']]))
                secondary_predicates = list(reversed([t for t in p if t.pos_ in ['ADP', 'AUX']]))
                predicate = primary_predicates + secondary_predicates
                if len(predicate)>0:
                    triples.append((p[0], predicate[0], p[-1]))

    triples = [(s, p, o) for (s, p, o) in triples if (s.text!=o.text)]

    new_triples = []
    for triple in triples:
        new_triple = []
        for token in triple:

            if token is None:
                new_triple.append(token)

            else:
                is_ent = False
                max_chunk = get_max_chunk(token)
                if isinstance(max_chunk, spacy.tokens.span.Span):
                    if len(max_chunk.ents)>0:
                        if max_chunk.text==max_chunk.ents[0].text:
                            is_ent = True

                if is_ent:
                    new_triple.append(max_chunk)
                else:
                    new_triple.append(token)
                    if token.text!=max_chunk.text:
                        new_triples.append((token, None, max_chunk))
        new_triples.append(new_triple)

    triples = [(s, p, o) for (s, p, o) in new_triples if (s.text!=o.text)]

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

    for idx, trp in enumerate(t):
        if trp.subj.text==trp.obj.text:
            t.pop(idx)

    return t
