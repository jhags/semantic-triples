import spacy

class Tag:

    def __init__(self, spacy_obj):
        self.span = spacy_obj
        self._type = self._get_type()
        self._is_ent = self._check_is_ent()
        self.text = self._get_text()

    def __repr__(self):
        return str(self.text)

    def _get_type(self):
        if isinstance(self.span, spacy.tokens.span.Span):
            return 'span'
        elif isinstance(self.span, spacy.tokens.token.Token):
            return 'token'
        else:
            return None

    def _check_is_ent(self):
        if self._type=='span':
            if len(self.span.ents)>0:
                if self.span.text==self.span.ents[0].text:
                    return True
        return False

    def _get_text(self):
        if self._type=='span':
            if self._is_ent:
                return ' '.join([t.text.lower() for t in self.span if t.pos_ not in ['DET']])
            elif self._is_ent is False:
                return ' '.join([t.lemma_.lower() for t in self.span if t.pos_ not in ['DET']])

        elif self._type=='token':
            if self._is_ent:
                return self.span.text.lower()
            elif self._is_ent is False:
                return self.span.lemma_.lower()

        return None

    def get_chunk(self, token):
        chunks = [c for c in token.doc.noun_chunks if token in c]
        if len(chunks)==0: return token
        return chunks[0]

    def get_max_chunk(self, token):
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

        return self.get_chunk(token)
