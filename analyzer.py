import argparse
import string
import json
from tqdm import tqdm

from engine import make_engine

# All the words we ignore because they are too general to give us informtaion about the product:
BLACKLIST = ['the', 'and', 'to', 'i', 'it', 'for', 'a', 'is', 'this', 'of', 'was', 'in', 'my', 'with', 'very',
                'that', 'not', 'as', 'than', 'its', 'but', 'nice', 'good', 'put', 'great', 'or', 'they', 'had',
                'only', 'love', 'would', 'have', 'perfect', 'can', 'our', 'has', 'will', 'use', 'all', 'at', 'be',
                'product', 'we', 'up', 'out', 'you', 'so', 'use', 'over']

def main():
    args = parse_args()
    analyzer = AdjectiveAnalyzer(args.engines)
    with open(args.json_file) as json_file:
        scrap_dict = json.loads(json_file.read())
    texts_list = text_list_from_dict(scrap_dict, args.text_to_analyze)
    adj_dict = analyzer.analyze(texts_list)
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
    """
    :param engine_names: A list of strings (for example: ['nltk', 'spacy'])
    """
    def __init__(self, engine_names):
        self.engines = []
        for name in engine_names:
            self.engines.append(make_engine(name))
            
    
    """
    :param texts_list: A list of strings
    :return: Dictionary where the keys are all the adjectives in all the texts,
    and the values are the amount of times each adjective appeared.
    """
    def analyze(self, texts_list):
        adj_dict = {}
        for text in tqdm(texts_list):
            # Remove punctuation and move to lowercase TODO: Maybe remove? Does the engines uses this information?
            text = text.translate(str.maketrans('', '', string.punctuation)).lower()
            is_adj = [] # This will be a list of lists
            for engine in self.engines:
                is_adj.append([pos == engine.get_adjective_symbol() for pos in engine.get_text_pos(text)])
                # We work with a boolean array
            for i, word in enumerate(text.split()):
                if word in BLACKLIST:
                    continue
                if all([adjs[i] for adjs in is_adj]):
                    # if all the engine think this is an adjective
                    if word in adj_dict:
                        adj_dict[word] += 1
                    else:
                        adj_dict[word] = 1
                
        # Sort the adjective dictionary before returning it
        return {k: v for k, v in sorted(adj_dict.items(), reverse=True, key=lambda item: item[1])}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--engines',
        help='Choose NLP analyzing engine or engines', type=str.lower, # This casts the input into lowercase
        metavar="adjective_engine", default='spacy', nargs='+', choices=['spacy', 'nltk', 'stanza']
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