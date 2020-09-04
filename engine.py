import nltk
import spacy
import stanza

def make_engine(engine_name):
    """
    Factory method, returns either NLTK, spaCy or stanza engine
    """
    legal_names = ['nltk', 'spacy', 'stanza']
    if engine_name not in legal_names:
        raise ValueError(f'Unrecognized engine name "{engine_name}".')
    elif engine_name == 'nltk':
        return NltkEngine()
    elif engine_name == 'spacy':
        return SpacyEngine()
    elif engine_name == 'stanza':
        return StanzaEngine()


class NltkEngine:
    """
    Constructor
    """
    def __init__(self):
        pass

    @staticmethod
    def get_adjective_symbol():
        return 'JJ'

    """
    Analyzes a text and returns it's POS
    :param text: A string
    :return: a list of POS in the same size as the number of words in the string 
    """
    def get_text_pos(self, text):
        tokens = nltk.word_tokenize(text)
        tagged_words = nltk.pos_tag(tokens)
        return [pair[1] for pair in tagged_words]

class SpacyEngine:
    """
    Constructor
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    @staticmethod
    def get_adjective_symbol():
        return 'ADJ'

    """
    Analyzes a text and returns it's POS
    :param text: A string
    :return: a list of POS in the same size as the number of words in the string 
    """
    def get_text_pos(self, text):
        doc = self.nlp(text)
        return [token.pos_ for token in doc]

        
class StanzaEngine:
    """
    Constructor
    """
    def __init__(self):
        self.nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos')


    @staticmethod
    def get_adjective_symbol():
        return 'ADJ'

    """
    Analyzes a text and returns it's POS
    :param text: A string
    :return: a list of POS in the same size as the number of words in the string 
    """
    def get_text_pos(self, text):
        doc = self.nlp(text)
        return [word.upos for sent in doc.sentences for word in sent.words]