
import os
import pandas as pd
import spacy
import string
from typing import TypeVar

spacyToken = TypeVar('spacy.tokens.token.Token')

root = os.path.abspath(os.path.join(__file__, "../.."))

# Get Spacy language packages
# nlp = spacy.load('en_core_web_lg')

class Node:

    def __init__(self, spacy_obj):
        self.span = spacy_obj

        # if isinstance(spacy_obj, spacy.tokens.span.Span):
        #     self.root = spacy_obj.root.lemma_
        #     self.text = ' '.join([t.lemma_.lower() for t in spacy_obj if t.pos_ not in ['DET']])
        #     self.idx = (spacy_obj.start_char, spacy_obj.end_char)

        if isinstance(spacy_obj, spacy.tokens.token.Token):
            self.phrase = self._get_full_phrase(spacy_obj)
            self.root = spacy_obj.text.lower()
            self.text = spacy_obj.lemma_.lower()
            self.idx = (spacy_obj.idx, spacy_obj.idx + len(spacy_obj.text))

        elif spacy_obj is None:
            self.root = ''
            self.phrase = ''
            self.text = 'None'
            self.idx = False

    def __repr__(self):
        return self.text

    @staticmethod
    def _get_full_phrase(spacy_token):
        doc = spacy_token.doc
        start_idx = spacy_token.idx
        chunk = [i for i in doc.noun_chunks if (i.start_char <= start_idx <= i.end_char)]
        if len(chunk)>0:
            return ' '.join([t.lemma_.lower() for t in chunk[0] if t.pos_ not in ['DET']])
            # return Node(chunk[0])
        return spacy_token.lemma_.lower()


class Triple:
    def __init__(self, subj, predicate, obj):
        self.subj = Node(subj)
        self.predicate = Node(predicate)
        self.obj = Node(obj)
        self.spo = (self.subj.text, self.predicate.text, self.obj.text)

    def __repr__(self):
        return f'({self.subj.phrase} -> {self.predicate.text} -> {self.obj.phrase})'

    def edges(self):
        if self.predicate.span is None:
            return [(self.subj.phrase, self.obj.phrase)]
        else:
            return [
                (self.subj.phrase, self.predicate.text),
                (self.predicate.text, self.obj.phrase)
                ]


def get_primary_predicate(subject: spacyToken):
    primary_predicate = subject.head

    if primary_predicate.pos_ in ['VERB', 'ADP', 'AUX']:
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
    lvl2_dep = ['prep', 'agent', 'relcl', 'acl']
    tokens = []
    for dep, toks in d.items():
        if dep in deps:
            tokens.extend(toks)

        elif dep in lvl2_dep:
            for tok in toks:
                t = get_objects(tok)
                tokens.extend(t)
    return tokens


def get_triples(doc):
    subjects = [i.root for i in doc.noun_chunks if i.root.dep_ in ['nsubj', 'nsubjpass']]
    triples = []
    for subject in subjects:

        primary_subject = subject
        primary_predicate = get_primary_predicate(primary_subject)
        primary_objects = get_objects(primary_predicate)

        for obj in primary_objects:
            triples.append(Triple(primary_subject, primary_predicate, obj))

        # Additional primary objects
        primary_objects = get_objects(primary_subject)
        for obj in primary_objects:
            triples.append(Triple(primary_subject, None, obj))

        # Secondary triples, where the primary subject is the same
        secondary_predicates = get_secondary_predicates(primary_predicate)
        for predicate in secondary_predicates:
            objs = get_objects(predicate)
            for obj in objs:
                triples.append(Triple(primary_subject, predicate, obj))

        # 2nd level objects
        objs = [x.obj.span for x in triples]
        for obj in objs:
            lvl2_objs = get_objects(obj)
            for obj2 in lvl2_objs:
                triples.append(Triple(obj, None, obj2))

        # 3rd level objects
        objs = [x.obj.span for x in triples]
        for obj in objs:
            lvl3_objs = get_objects(obj)
            for obj3 in lvl3_objs:
                triples.append(Triple(obj, None, obj3))

    return triples
