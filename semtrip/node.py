import spacy

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
            self.phrase = None
            self.text = None
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