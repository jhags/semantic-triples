# semantic-triples
Turn text into a network of semantic triples.

## Install
Since this isn't published on PyPI, install from the repo with:
```python
python -m pip install git+https://github.com/jhags/semantic-triples.git
```

## Demo

The following is a little demo on how to get started quick using text from wikipedia.

```python
from semnet import Semnet
import spacy

import wikipedia

page = wikipedia.page('COVID-19 pandemic')
text = page.summary

# Download spacy model using CLI
# > python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

s = Semnet(text, nlp)
s.get_triples()
s.get_graph()

edges = s.get_graph_data()
nodes = s.get_graph_nodes()

edges.to_csv('edges.csv', index=False)
nodes.to_csv('nodes.csv', index=False)
s.save_graph('graph.gexf')
```