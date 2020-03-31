import requests
import lxml
from lxml import html
from nltk.corpus import wordnet as wn
from tqdm import tqdm # for pretty progress bars

URL = "https://www.amazon.com/Happy-Haystack-Stainless-Bottle-Design/product-reviews/B07YL48NZQ/&reviewerType=all_reviews"
URL = "https://www.amazon.com/Sleepwish-Blanket-Cartoon-Pattern-Blankets/product-reviews/B075L8PXM1/ref=cm_cr_arp_d_viewpnt_lft?ie=UTF8&reviewerType=all_reviews"

SEARCH_URL = "https://www.amazon.com/s?k={SEARCH_TERM}&page={PAGE_NUM}"
AMAZON_PREFIX = "https://www.amazon.com"

PRODUCT_XPATH = '//a[@class="a-link-normal a-text-normal"]'
REVIEW_BUTTON_XPATH = '//a[@class="a-link-emphasis a-text-bold"]'
REVIEW_TEXT_XPATH = '//span[@class="a-size-base review-text review-text-content"]'

def get_all_reviews(url):
    page = requests.get(url, headers={"User-Agent":"Defined"})
    doc = lxml.html.fromstring(page.content)
    text = ""

    review_spans = doc.xpath(REVIEW_TEXT_XPATH)
    for rev in review_spans:
        for i in rev:
            text += str(i.text) + " "
    
    return text

def text_to_adj_dict(text):
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

class Navigator():
    def __init__(self, product_name):
        self.product_name = product_name.replace(' ', '+')

    def get_products(self, n):
        """
        get the first n (or maximum) products in search results
        :param int n: The number of webpages to return
        :return: a list of webpages
        """
        products_urls = []
        i = 1
        while(len(products_urls) < n):
            url = SEARCH_URL.format(SEARCH_TERM=self.product_name, PAGE_NUM=i)
            page = requests.get(url, headers={"User-Agent":"Defined"})
            self.doc = lxml.html.fromstring(page.content)
            products_a = self.doc.xpath(PRODUCT_XPATH)
            print(f"In page {i} there are {len(products_a)} products.")
            if (len(products_a) == 0):
                # This means we reached a page without products
                break 
            for p in products_a:
                if len(products_urls) > n: break # If we already have n products we can return
                if not (p.get('href') in products_urls): # For some reason we get duplicates sometime
                    products_urls.append(p.get('href'))
            i += 1
        print(f"found {len(products_urls)} items.")
        return products_urls

    def get_review_pages(self, product_webpage):
        """
        return a list of URLs of the product
        """
        get_all_reviews

    def get_adj_dict(self, review_pages):
        text = ""
        for page in review_pages:
            text += get_all_reviews(page)
        return text_to_adj_dict(text)

if __name__ == "__main__":
    nav = Navigator("table")
    products_urls = nav.get_products(20)
    all_review = ""
    for prod_url in tqdm(products_urls):
        rev_url = prod_url.replace("/dp/", "/product-review/")
        all_review += (" "+get_all_reviews(AMAZON_PREFIX+rev_url))
    adj_dict = text_to_adj_dict(all_review)
    print(adj_dict)
    