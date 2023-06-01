import os
from stanfordnlp.server import CoreNLPClient
from nltk.tag import StanfordNERTagger

stanford_dir = 'Users/moneim/NLG_Assignment3/stanford-corenlp-4.5.1'


model_name = 'english.all.3class.distsim.crf.ser.gz'
model_path = os.path.join('/Users/moneim/NLG_Assignment3/stanford-ner-2020-11-17', 'classifiers', model_name)
jar_path = os.path.join('/Users/moneim/NLG_Assignment3/stanford-ner-2020-11-17', 'stanford-ner.jar')

import spacy
nlp = spacy.load("en_core_web_sm")

# set up the client
os.environ['CORENLP_HOME'] = 'Users/moneim/NLG_Assignment3/stanford-corenlp-4.5.1'
client = CoreNLPClient(endpoint='http://localhost:9000',annotators=['ner'], timeout=30000, memory='4G')

# define a function to extract football players' names
def extract_player_names(text):
    """
    Extracts football players' names from a string using Stanford NER.
    """
    players = []
    ann = client.annotate(text)
    for sentence in ann.sentence:
        for token in sentence.token:
            (players.append(token.word) if token.ner == 'PERSON' else None)
    return players


def extract_club_names(text):
    """
        Extracts club names from a string using Stanford NER.
    """
    ner_tagger = StanfordNERTagger(model_path, jar_path, encoding='utf8')
    tagged_entities = ner_tagger.tag(text.split())
    return list([entity[0] for entity in tagged_entities if entity[1] == 'ORGANIZATION' or entity[1] == 'LOCATION'])



