import spacy

class Node:

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
                return ' '.join([t.text.lower() for t in self.span if t.pos_ not in ['DET', 'PUNCT']])
            elif self._is_ent is False:
                return ' '.join([t.lemma_.lower() for t in self.span if t.pos_ not in ['DET', 'PUNCT']])

        elif self._type=='token':
            if self._is_ent:
                return self.span.text.lower()
            elif self._is_ent is False:
                return self.span.lemma_.lower()

        return None
