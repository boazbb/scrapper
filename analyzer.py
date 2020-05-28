import argparse
import json
from nltk.corpus import wordnet as wn
import spacy

def main():
    args = parse_args()
    analyzer = AdjectiveAnalyzer(args.engine)
    with open(args.json_file) as json_file:
        review_dict = json.loads(json_file.read())
    print(analyzer.analyze(review_dict))

class AdjectiveAnalyzer:
    def nltk_text_to_adj_dict(review_dict):
        adj_dict = {}
        for reviews in review_dict:
            for text in reviews:
                text = text.lower()
                for word in text.split():
                    if word in adj_dict:
                        adj_dict[word] += 1
                    else:
                        # Find the synonims and see what their POS is:
                        for tmp in wn.synsets(word):
                            if tmp.name().split('.')[0] == word:
                                if tmp.pos() == 'a':
                                    adj_dict[word] = 1
        # return sortrd by value:
        return {k: v for k, v in sorted(adj_dict.items(), reverse=True, key=lambda item: item[1])}

    def spacy_text_to_adj_dict(review_dict):
        adj_dict = {}
        nlp = spacy.load("en_core_web_sm")
        for reviews in review_dict:
            for text in reviews:
                text = text.lower()
                doc = nlp(text)
                for token in doc:
                    if token.text in adj_dict:
                        adj_dict[token.text] += 1
                    else:
                        # Find the synonims and see what their POS is:
                        if token.pos_ == "ADJ":
                            adj_dict[token.text] = 1
        # return sortrd by value:
        return {k: v for k, v in sorted(adj_dict.items(), reverse=True, key=lambda item: item[1])}

    adj_funcs = {'spacy': spacy_text_to_adj_dict, 'nltk': nltk_text_to_adj_dict}
        
    def __init__(self, engine='spacy'):
        self.analyze = AdjectiveAnalyzer.adj_funcs[engine]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--engine',
        help='Choose NLP analyzing engine (NLTK or spaCy)', type=str.lower, # This casts the input into lowercase
        metavar="adjective_engine", default='spacy', choices=['nltk', 'spacy']
        )
    parser.add_argument(
        '-j', '--json-file',
        help='The path of the JSON file of reviews to analyze',
        metavar="json_path", required=True
        )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()

#TODO: In the dictionary, save a pointer to the original text