import numpy as np
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pandas import DataFrame

WORDS = [
    'colorful', 'vibrant', 'inflatable', 'crushed', 'indoor', 'rustic', 'decorative', 'lovely',
    'floral', 'classic',  'African', 'roomy', 'horizontal', 'vertical', 'Indian', 'portable',
    'adjustable', 'medical', 'elderly', 'wobbly', 'hot', 'frozen', 'accurate', 'burnt', 'warm'
]

CLASSES = ['ball', 'vase', 'birdcage', 'table', 'oven']

def main():
    agreement(["noam", "shaul", "michael", "david", "yael", "adi", "naomi"], 'Everyone')
    agreement(["david", "yael", "adi", "naomi"], 'Hebrew Spekaers')
    agreement(["noam", "michael", "shaul"], 'English Spekaers')


def agreement(people, title):
    table, n = get_table(people)
    pjs = table.sum(axis=0) / (len(WORDS) * n) # Trivial from experiment
    square = np.square(table)
    pis = (square.sum(axis=1) - n)/ (n*(n-1))
    p_mean = pis.mean()
    pe_mean = np.square(pjs).mean()
    kappa = (p_mean - pe_mean)/(1 - pe_mean)
    show_agreement(pis, kappa, title)
    print(kappa)

def show_agreement(pis, kappa, title):
    sns.set_style("darkgrid", {"axes.facecolor": ".9"})
    fig, axs = plt.subplots(3, 1)
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:purple', 'tab:red']
    for i in range(2):
        b = axs[i].bar(WORDS[i*8:(i+1)*8], pis[i*8:(i+1)*8])
        for j in range(8):
            b[j].set_color(colors[(i*8+j)//5])
    i += 1
    b = axs[i].bar(WORDS[i*8:], pis[i*8:])
    for j in range(9):
            b[j].set_color(colors[(i*8+j)//5])
    fig.suptitle(f'{title}\nAgreement of specific words, overall $\kappa = {kappa:.2f}$')
    
    patches = [mpatches.Patch(color=colors[i], label=CLASSES[i]) for i in range(5)]
    plt.legend(handles=patches)
    plt.show()

def get_table(ppl=["noam", "shaul", "michael", "david", "yael", "adi", "naomi"]):
    table = np.zeros((len(WORDS), len(CLASSES)))
    with open("human.json", 'r') as f:
        j = json.loads(f.read())
    for person in j:
        if person in ppl:
            for item in j[person]:
                for word in j[person][item]:
                    table[WORDS.index(word)][CLASSES.index(item)] += 1
    return table, len(ppl)


if __name__ == "__main__":
    main()