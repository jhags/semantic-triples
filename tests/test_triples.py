
import os
import sys
import pytest
import spacy

root = os.path.abspath(os.path.join(__file__, "../.."))
sys.path.append(root + r'/scripts')

# pylint: disable=import-error
from semantic_triples import get_triples

# Get Spacy language packages
nlp = spacy.load('en_core_web_sm')

def test_doc1():
    doc = nlp('A rare black squirrel has become a regular visitor to a suburban garden')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('squirrel', 'to', 'garden'), ('squirrel', 'become', 'visitor')]
    assert triples == expected


def test_doc2():
    doc = nlp('The man stood beside the large fridge')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('man', 'stood', 'fridge')]
    assert triples == expected


def test_doc3():
    doc = nlp('The man was standing beside the larger fridge')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('man', 'standing', 'fridge')]
    assert triples == expected


def test_doc4():
    doc = nlp('the quick brown fox jumps over the lazy dog')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('fox', 'jumps', 'dog')]
    assert triples == expected


def test_doc5():
    doc = nlp('Mike said triples can be objects')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('Mike', 'said', 'be'), ('triple', 'be', 'objects')]
    assert triples == expected


def test_doc6():
    doc = nlp('London is the capital city of the United Kingdom')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('London', 'of', 'Kingdom'), ('London', 'is', 'city')]
    assert triples == expected


def test_doc7():
    doc = nlp('comment were related to persistent follow ups from accounting')
    triples = [t.spo for t in get_triples(doc)]

    expected = [('comment', 'from', 'accounting'), ('comment', 'related', 'ups')]
    assert triples == expected
