
import os
import pandas as pd
import spacy
import string


root = os.path.abspath(os.path.join(__file__, "../.."))

# Get Spacy language packages
# nlp = spacy.load('en_core_web_lg')

class Node:

    def __init__(self, spacy_obj):
        self.span = spacy_obj

        if isinstance(spacy_obj, spacy.tokens.span.Span):
            self.root = spacy_obj.root.text
            self.phrase = ' '.join([t.text for t in spacy_obj if t.pos_ not in ['DET']])
            self.text = ' '.join([t.lemma_ for t in spacy_obj if t.pos_ not in ['DET']])
            self.idx = (spacy_obj.start_char, spacy_obj.end_char)

        elif isinstance(spacy_obj, spacy.tokens.token.Token):
            self.root = spacy_obj.text
            self.phrase = spacy_obj.text
            self.text = spacy_obj.text
            self.idx = (spacy_obj.idx, spacy_obj.idx + len(spacy_obj.text))

        elif spacy_obj is None:
            self.root = ''
            self.phrase = ''
            self.text = 'None'
            self.idx = False

    def __repr__(self):
        return self.text


class Triple:
    def __init__(self, subj, predicate, obj):
        self.subj = self._get_full_phrase(subj)
        self.predicate = self._get_full_phrase(predicate)
        self.obj = self._get_full_phrase(obj)
        self.spo = (self.subj.text, self.predicate.text, self.obj.text)

    def __repr__(self):
        return f'({self.subj} -> {self.predicate} -> {self.obj})'

    @staticmethod
    def _get_full_phrase(spacy_token):
        if spacy_token is None:
            return Node(spacy_token)
        doc = spacy_token.doc
        start_idx = spacy_token.idx
        chunk = [i for i in doc.noun_chunks if (i.start_char <= start_idx <= i.end_char)]
        if len(chunk)>0:
            return Node(chunk[0])
        return Node(spacy_token)

    def edges(self):
        if self.predicate.span is None:
            return [(self.subj.text, self.obj.text)]
        else:
            return [
                (self.subj.text, self.predicate.text),
                (self.predicate.text, self.obj.text)
                ]


def remove_punctuation(text_str):
    chars = string.punctuation + '−'
    for char in chars:
        text_str = text_str.replace(char, ' ')
    return ' '.join(text_str.split())


def find_child_objects(spacy_token):
    children = list(spacy_token.children)
    children_dep = [child.dep_ for child in children]
    children_dict = dict(zip(children_dep, children))

    primary_deps = ['pobj', 'dobj', 'attr', 'ccomp']
    secondary_deps = ['prep', 'agent', 'relcl', 'acl']
    for dep in (primary_deps + secondary_deps):
        token = children_dict.get(dep)
        if token is not None:
            if dep in secondary_deps:
                return find_child_objects(token)
            return token


def find_secondary_predicate(spacy_token):
    for child in list(spacy_token.children):
        if child.dep_ in ['prep', 'agent', 'relcl', 'acl']: return child


def get_subjects(node_dict):
    subjects = []
    for v in node_dict.values():
        if v['type']=='subject':
            chunk = v['object']
            subjects.append((chunk.root, chunk))
    return subjects


def get_triples(doc):
    subjects = [i.root for i in doc.noun_chunks if i.root.dep_ in ['nsubj', 'nsubjpass']]

    triples = []
    for subject in subjects:
        primary_predicate, primary_obj = None, None
        primary_predicate = subject.head

        if primary_predicate.pos_ in ['VERB', 'ADP', 'AUX']:
            if primary_predicate.pos_ in ['ADP']:
                if primary_predicate.head.pos_ in ['VERB']:
                    primary_predicate = primary_predicate.head

        primary_obj = find_child_objects(primary_predicate)
        triples.append(Triple(subject, primary_predicate, primary_obj))

        if primary_obj is not None:
            level2_obj = find_child_objects(primary_obj)
            level2_predicate = find_secondary_predicate(primary_obj)

        if (level2_obj is not None) & (level2_predicate is not None):
            triples.append(Triple(subject, level2_predicate, level2_obj))

        secondary_predicates = []
        for child in list(subject.children):
            if child.dep_ in ['prep', 'agent', 'relcl', 'acl', 'conj', 'appos']: 
                secondary_predicates.append(child)

        sec_objs = []
        for p in secondary_predicates:
            sec_objs.append(find_child_objects(p))

        for (p, o) in zip(secondary_predicates, sec_objs):
            if (p is not None) & (o is None):
                p, o = o, p
            triples.append(Triple(subject, p, o))
    return triples
