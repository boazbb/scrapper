import numpy as np
import fasttext
from scipy.spatial import distance
from tqdm import tqdm
import io
import matplotlib.pyplot as plt
import copy
import os
import gensim.downloader as api
from gensim.models import KeyedVectors
from gensim.downloader import base_dir

GOOGLE_NEWS_PATH = "C:\\Users\\avivim100\\gensim-data\\word2vec-google-news-300"

NUM_WORDS = 200000

def main():
    plt.style.use('seaborn')
    # data = FastTextVecs()
    data = GensimGoogleVecs()
    table_birdcage_bars(data)
    table_oven_bars(data)
    lazer_birdcage_bars(data)

def lazer_birdcage_bars(data):
    lazer_adjs = ['accurate', 'bright', 'right', 'light', 'visible']
    cage_adjs = ['large', 'big', 'hard', 'strong', 'huge']

    plot_word_bars(data, 'laser', 'laser', lazer_adjs)
    plot_word_bars(data, 'birdcage', 'birdcage', cage_adjs)
    plot_word_bars(data, 'laser', 'birdcage', cage_adjs)
    plot_word_bars(data, 'birdcage', 'laser', lazer_adjs)

def table_oven_bars(data):
    table_adjs = ['heavy', 'cheap', 'light', 'solid', 'stable']
    oven_adjs = ['easy', 'big', 'old', 'new', 'fine']

    plot_word_bars(data, 'table', 'table', table_adjs)
    plot_word_bars(data, 'oven', 'oven', oven_adjs)
    plot_word_bars(data, 'table', 'oven', oven_adjs)
    plot_word_bars(data, 'oven', 'table', table_adjs)

def table_birdcage_bars(data):
    table_adjs = ['heavy', 'cheap', 'light', 'solid', 'stable']
    cage_adjs = ['large', 'big', 'hard', 'strong', 'huge']
    plot_word_bars(data, 'table', 'table', table_adjs)
    plot_word_bars(data, 'birdcage', 'birdcage', cage_adjs)
    plot_word_bars(data, 'table', 'birdcage', cage_adjs)
    plot_word_bars(data, 'birdcage', 'table', table_adjs)

def plot_word_bars(data, original_word, scrapped_word, words):
    sims = list(map(lambda w: data.sim(original_word, w), words))
    width = 0.35       # the width of the bars: can also be len(x) sequence
    fig, ax = plt.subplots()

    ax.bar(words, sims)

    ax.set_ylabel('Similarity (Cosine Distance of the vectors)')
    ax.set_title(f'Similarity of Scrapped Adjectives from "{scrapped_word}" to "{original_word}", average={"%.2f" % (sum(sims)/len(sims))}')
    ax.set_ylim(0, 1)

    plt.show()


class FastTextVecs:
    def __init__(self):
        fin = io.open("vecs", 'r', encoding='utf-8', newline='\n', errors='ignore')
        n, d = map(int, fin.readline().split())
        data = {}
        it = iter(fin)
        for i in tqdm(range(NUM_WORDS)):
            line = next(it)
            tokens = line.rstrip().split(' ')
            data[tokens[0]] = map(float, tokens[1:])
        self.dict = data

    def __getitem__(self, word):
        return np.array(list(copy.deepcopy(self.dict[word])))

    def sim(self, word1, word2):
        print(f"Words are {word1} and {word2}")
        print(f"Vecs are {self[word1]} and {self[word2]}")
        return distance.cosine(normalize(np.array(self[word1])), normalize(np.array(self[word2])))

class GensimGoogleVecs:
    def __init__(self):
        self.model = ord_vectors = api.load("word2vec-google-news-300")

    def __getitem__(self, word):
        return self.model[word]

    def sim(self, word1, word2):
        print(f"Words are {word1} and {word2}")
        print(f"Vecs are {self[word1]} and {self[word2]}")
        return distance.cosine(normalize(np.array(self[word1])), normalize(np.array(self[word2])))

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

if __name__ == "__main__":
    main()
