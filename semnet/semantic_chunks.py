import os
import spacy
from typing import TypeVar

from .node import Node

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


def get_tags(doc):
    objs = list(set([token for token in doc if token.pos_ in ['NOUN', 'PROPN']]))
    objs = list(set([get_max_chunk(i) for i in objs]))

    nodes = [Node(token) for token in objs]

nodes[-2].span.root
[node.span.root for node in nodes if node._type=='span']