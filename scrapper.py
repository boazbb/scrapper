import requests
import lxml
from lxml import html
from tqdm import tqdm # for pretty progress bars
import argparse
import json

from nltk.corpus import wordnet as wn
import spacy

URL = "https://www.amazon.com/Happy-Haystack-Stainless-Bottle-Design/product-reviews/B07YL48NZQ/&reviewerType=all_reviews"
URL = "https://www.amazon.com/Sleepwish-Blanket-Cartoon-Pattern-Blankets/product-reviews/B075L8PXM1/ref=cm_cr_arp_d_viewpnt_lft?ie=UTF8&reviewerType=all_reviews"

SEARCH_URL = "https://www.amazon.com/s?k={SEARCH_TERM}&page={PAGE_NUM}"
CAT_SEARCH_URL = "https://www.amazon.com/s?k={SEARCH_TERM}&i={CATEGORY}&page={PAGE_NUM}"
AMAZON_PREFIX = "https://www.amazon.com"

PRODUCT_XPATH = '//a[@class="a-link-normal a-text-normal"]'
REVIEW_BUTTON_XPATH = '//a[@class="a-link-emphasis a-text-bold"]'
REVIEW_COUNT_XPATH = '//span[@data-hook="cr-filter-info-review-count"]'
REVIEW_TEXT_XPATH = '//span[@class="a-size-base review-text review-text-content"]'

headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }

# hpc is health and household. just add &i={} in the url
categories = ["arts-crafts", "automotive", "baby-products", "beauty", "stripbooks", "computers", "digital-music", "electronics", "digital-text",
                "instant-video", "fashion-womens", "fashion-mens", "fashion-girls", "fashion-boys", "deals", "hpc", "kitchen", "industrial", 
                "luggage", "movies-tv", "music", "pets", "software", "sporting", "tools", "toys-and-games", "videogames"]

REVIEW_IN_PAGE = 10

def main():
    args = parse_args()
    if (args.list_categories):
        # Print all possible categories
        print('All possible categories:')
        print('  '+'\n  '.join(categories))
        exit(0)
    nav = Navigator(args.keyword, args.category, args.review_pages)
    products = nav.get_products(args.pages)
    all_review = ""
    for prod in tqdm(products):
        rev_url = prod.url.replace("/dp/", "/product-review/")
        print(f"The URL we are looking for:\n{AMAZON_PREFIX+rev_url}\n")
        all_review += (" "+nav.get_product_review_text(AMAZON_PREFIX+rev_url))
    adj_dict = adj_funcs[args.engine](all_review)
    print(adj_dict)
    if args.dump:
        dump_file = open(args.dump, 'w')
        dump_file.write(json.dumps(adj_dict))

# Eventually maybe turn into a class

def nltk_text_to_adj_dict(text):
    text = text.lower()
    adj_dict = {}
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

def spacy_text_to_adj_dict(text):
    text = text.lower()
    adj_dict = {}
    nlp = spacy.load("en_core_web_sm")
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

class Product():
    # Product have the URL and a List of review text
    def __init__(self, url):
        self.url = url
        self.review_texts = []

    def add_review_text(self, text):
        self.review_texts.append(text)

    @staticmethod
    def url_list_to_product_list(url_list):
        product_list = []
        for url in url_list:
            product_list.append(Product(url))
        return product_list


class Navigator():
    def __init__(self, product_name, category=None, max_review_pages=None):
        self.product_name = product_name.replace(' ', '+')
        self.category = category
        if category and category not in categories:
            print("Wrong category, doing general search instead.")
            self.category = None
        self.max_review_pages = max_review_pages

    def get_url(self, page_num):
        if self.category:
            return CAT_SEARCH_URL.format(SEARCH_TERM=self.product_name, CATEGORY=self.category, PAGE_NUM=page_num)
        else:
            return SEARCH_URL.format(SEARCH_TERM=self.product_name, PAGE_NUM=page_num)


    def get_products(self, n):
        """
        get the first n (or maximum) products in search results
        :param int n: The number of webpages to return
        :return: a list of webpages
        """
        products_urls = []
        i = 1
        while(len(products_urls) < n):
            url = self.get_url(i)
            print(f"url is {url}")
            page = requests.get(url, headers=headers)
            self.doc = lxml.html.fromstring(page.content)
            products_a = self.doc.xpath(PRODUCT_XPATH)
            print(f"In page {i} there are {len(products_a)} products.")
            if (len(products_a) == 0):
                # This means we reached a page without products
                break 
            for p in products_a:
                if len(products_urls) > n: break # If we already have n products we can return
                # For some reason we get duplicates sometime, also another search result k=SEARCHTERM
                if not (p.get('href') in products_urls) and not p.get('href').startswith('/s?k='):
                    products_urls.append(p.get('href'))
            i += 1
        print(f"found {len(products_urls)} items.")
        print(products_urls)
        return Product.url_list_to_product_list(products_urls)

    def get_all_reviews_from_page(self, url):
        page = requests.get(url, headers=headers)
        doc = lxml.html.fromstring(page.content)
        text = ""

        review_spans = doc.xpath(REVIEW_TEXT_XPATH)
        for rev in review_spans:
            for i in rev:
                text += str(i.text) + " "
    
        return text

    def get_product_review_text(self, product_webpage):
        """
        return a list of URLs of the product
        """
        # Find the overall number of reviews:
        page = requests.get(product_webpage, headers=headers)
        doc = lxml.html.fromstring(page.content)
        count = int(doc.xpath(REVIEW_COUNT_XPATH)[0].text.split()[-2].replace(',',''))
        page_number = - (-count // REVIEW_IN_PAGE) # Rounding Up
        if self.max_review_pages:
            page_number = min(page_number, self.max_review_pages)
        page_suffix = "&pageNumber={num}"
        text = ''
        for i in tqdm(range(1, page_number+1)):
        # Get the review text:
            new_text = self.get_all_reviews_from_page(product_webpage+page_suffix.format(num=i))
            text += new_text
        return text

def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-l', '--list_categories',
        help='Use this flag to list all possible categories.',
        action='store_true'
        )
    group.add_argument(
        '-k', '--keyword',
        help='The keyword to search for'
        )
    parser.add_argument(
        '-c', '--category',
        help='The amazon category to search in',
        default=None
        )
    parser.add_argument(
        '-p', '--pages',
        help='Maximal number of search pages to go through',
        type=int, default=1000
        )
    parser.add_argument(
        '-d', '--dump',
        help='Save the dictionary to dump_file (using JSON)',
        metavar="dump_file", default=None
        )
    parser.add_argument(
        '-e', '--engine',
        help='Choose NLP analyzing engine (NLTK or spaCy)', type=str.lower, # This casts the input into lowercase
        metavar="adjective_engine", default='spacy', choices=['nltk', 'spacy']
        )
    parser.add_argument(
        '-rp', '--review-pages',
        help='Maximum number of review pages to search for in every product', type=int
        )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()

#TODO: Pass an argument for max reviews (and not max pages)
#TODO: Add Product Information Text w. different dictionaries
#TODO: Saving the url of the products, with a dict per URL
#TODO: In the dictionary, save a pointer to the original text