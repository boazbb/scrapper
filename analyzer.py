import argparse
import string
import json

from nltk.corpus import wordnet as wn
import spacy

BLACKLIST = ['great', 'good', 'nice', 'on', 'enough', 'better']

def main():
    args = parse_args()
    analyzer = AdjectiveAnalyzer(args.engine)
    with open(args.json_file) as json_file:
        scrap_dict = json.loads(json_file.read())
    texts_list = text_list_from_dict(scrap_dict, args.text_to_analyze)
    analyzer.analyze(texts_list)
    adj_dict = analyzer.get_adj_dict()
    print(adj_dict)
    if (args.output_file):
        with open(args.output_file, 'w') as save_file:
            save_file.write(json.dumps(adj_dict))

def text_list_from_dict(scrap_dict, text_type):
    text_list = []
    if text_type in ['info', 'all']:
        for product in scrap_dict:
            info = scrap_dict[product]["Product Info"]
            text_list += info['Bullets']
            text_list += [info["Product Description"]]
    if text_type in ['reviews', 'all']:
        for product in scrap_dict:
            text_list += scrap_dict[product]["Reviews"]
    return text_list


class AdjectiveAnalyzer:
    
    def __init__(self, engine='spacy'):
        self.engine = engine
        if engine == 'spacy' or  engine == 'both':
            self.nlp = spacy.load("en_core_web_sm")
        self.adj_dict = {}

    def nltk_is_adj(self, word):
        for tmp in wn.synsets(word):
            if tmp.name().split('.')[0] == word:
                if tmp.pos() == 'a':
                    return True
        return False

    def nltk_analyze_review(self, review):
        for word in review.split():
            if word in BLACKLIST:
                continue
            if word in self.adj_dict:
                self.adj_dict[word] += 1
            else:
                # Find the synonims and see what their POS is:
                if self.nltk_is_adj(word):
                    self.adj_dict[word] = 1

    def spacy_analyze_review(self, review):
        doc = self.nlp(review)
        for token in doc:
            if token.text in BLACKLIST:
                continue
            if token.text in self.adj_dict:
                self.adj_dict[token.text] += 1
            else:
                if token.pos_ == "ADJ":
                    self.adj_dict[token.text] = 1

    def both_analyze_review(self, review):
        doc = self.nlp(review)
        for token in doc:
            if token.text in BLACKLIST:
                continue
            if token.text in self.adj_dict:
                self.adj_dict[token.text] += 1
            else:
                if token.pos_ == "ADJ" and self.nltk_is_adj(token.text):
                    self.adj_dict[token.text] = 1


    def analyze(self, texts_list):
        # Figure out which function to use for analyzing the reviews
        if self.engine == "spacy":
            analyze_review = self.spacy_analyze_review
        elif self.engine == "nltk":
            analyze_review = self.nltk_analyze_review
        elif self.engine == "both":
            analyze_review = self.both_analyze_review
        else:
            raise ValueError("Unrecognised NLP engine.")

        for text in texts_list:
            # Remove punctuation and move to lowercase
            analyze_review(text.translate(str.maketrans('', '', string.punctuation)).lower())

    def get_adj_dict(self):
        # Sort the adjective dictionary before returning it
        return {k: v for k, v in sorted(self.adj_dict.items(), reverse=True, key=lambda item: item[1])}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--engine',
        help='Choose NLP analyzing engine (NLTK, spaCy or both)', type=str.lower, # This casts the input into lowercase
        metavar="adjective_engine", default='spacy', choices=['nltk', 'spacy', 'both']
        )
    parser.add_argument(
        '-j', '--json-file',
        help='The path of the JSON file of reviews to analyze',
        metavar="json_path", required=True
        )
    parser.add_argument(
        '-o', '--output-file',
        help='The path of the JSON file of the output',
        metavar="output_path", default=None
        )
    parser.add_argument(
        '--text-to-analyze',
        help='Choose text to analyze (reviews, info or both)', type=str.lower, # This casts the input into lowercase
        metavar="text_type", default='reviews', choices=['reviews', 'info', 'all']
        )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()

#TODO: In the dictionary, save a pointer to the original text