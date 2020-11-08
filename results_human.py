import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from pandas import DataFrame
import os
import json
import random
from collections import defaultdict


ITEMS = ['ball', 'vase', 'birdcage', 'table', 'oven']

WORDS = {
    'ball': ['colorful', 'vibrant', 'inflatable', 'crushed', 'indoor'],
    'vase': ['rustic', 'decorative', 'lovely', 'floral', 'classic'],
    'birdcage': ['African', 'roomy', 'horizontal', 'vertical', 'Indian'],
    'table': ['portable', 'adjustable', 'medical', 'elderly', 'wobbly'],
    'oven': ['hot', 'frozen', 'accurate', 'burnt', 'warm'],
}

NUMBERING = [
    'colorful', 'vibrant', 'inflatable', 'crushed', 'indoor', 'rustic', 'decorative', 'lovely',
    'floral', 'classic',  'African', 'roomy', 'horizontal', 'vertical', 'Indian', 'portable',
    'adjustable', 'medical', 'elderly', 'wobbly', 'hot', 'frozen', 'accurate', 'burnt', 'warm'
]

NEGLIGIBLE = 5

def main():
    print_conf_matrix()

def print_word_matrix():
    table = np.zeros((25, 25))
    words = subvert()
    for word in words:
        for item in words[word]:
            for sim_word in WORDS[item]: # Very informative names!
                table[NUMBERING.index(word)][NUMBERING.index(sim_word)] += 1
    # for line in table:
    #     line /= line.sum()
    show_heatmap(table, NUMBERING, NUMBERING, 'Human', 'Scrapper', 'Apperences in related')

def subvert():
    words = defaultdict(lambda: [])
    with open("human.json", 'r') as f:
        j = json.loads(f.read())
        for person in j:
            for item in j[person]:
                for word in j[person][item]:
                    words[word].append(item)
                    print(word)
    return words

def print_conf_matrix():
    table = np.zeros((5, 5))
    with open("human.json", 'r') as f:
        j = json.loads(f.read())
        for person in j:
            for item in j[person]:
                for word in j[person][item]:
                    scrapper_class = NUMBERING.index(word) // 5
                    human_class = ITEMS.index(item)
                    table[scrapper_class][human_class] += 1
    for line in table:
        line /= line.sum()
    show_heatmap(table, ITEMS, ITEMS, 'Human', 'Scrapper', 'Percent (Line-Normalized)')
                    

def print_human_mat():
    table = np.zeros((5, 25))
    with open("human.json", 'r') as f:
        j = json.loads(f.read())
        for person in j:
            for item in j[person]:
                for word in j[person][item]:
                    table[ITEMS.index(item)][NUMBERING.index(word)] += 1
    table /= 7
    show_heatmap(table, ITEMS, NUMBERING)
    table = np.zeros((5, 25))
    for item in WORDS:
        for word in WORDS[item]:
            table[ITEMS.index(item)][NUMBERING.index(word)] += 1
    show_heatmap(table, ITEMS, NUMBERING)

def show_heatmap(table, index, columns, xl='', yl='', title=''):
    df_cm = DataFrame(table, index=index, columns=columns)
    ax = sn.heatmap(df_cm, cmap='Oranges', annot=True)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.5, top - 0.5)
    ax.set(xlabel=xl, ylabel=yl, title=title)
    plt.show()

def validate():
    with open("human.json", 'r') as f:
        j = json.loads(f.read())
    for person in j:
        print(f"\nfor person {person}")
        for item in WORDS:
            for word in WORDS[item]:
                c = all_sub(j[person]).count(word) 
                if c == 0:
                    print(f"\t{word} not in.")
                elif c == 1:
                    pass
                else:
                    print(f"\t{word} in {c} times.")

def all_sub(d):
    a = []
    for key in d:
        a += d[key]
    return a


def randomizer():
    words = []
    for i in ITEMS:
        words += WORDS[i]
    print(words)
    print(random.shuffle(words))
    print(words)

def find_words():
    plt.style.use('seaborn')
    jsons = {}
    for item in ITEMS:
        file = open(item+"_output.json", 'r')
        jsons[item] = json.loads(file.read())
    
    unique_words = {}

    for item in ITEMS:
        unique_words[item] = []
        other_items = [i for i in ITEMS if i != item]
        for word in jsons[item]:
            unique = True
            for o in other_items:
                if word in jsons[o]:
                    if jsons[o][word] > NEGLIGIBLE:
                        unique = False
                        break
            if unique:
                unique_words[item].append(word)

    for k in unique_words:
        print(f"\nFor word {k}:")
        for i in range(30):
            print(f"  {unique_words[k][i]}")

if __name__ == "__main__":
    main()
