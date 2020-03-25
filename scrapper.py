import requests
import lxml
from lxml import html
from nltk.corpus import wordnet as wn

URL = "https://www.amazon.com/Happy-Haystack-Stainless-Bottle-Design/product-reviews/B07YL48NZQ/&reviewerType=all_reviews"
URL = "https://www.amazon.com/Sleepwish-Blanket-Cartoon-Pattern-Blankets/product-reviews/B075L8PXM1/ref=cm_cr_arp_d_viewpnt_lft?ie=UTF8&reviewerType=all_reviews"
XPATH = '//span[@class="a-size-base review-text review-text-content"]'

def get_all_reviews(url):
    page = requests.get(url, headers={"User-Agent":"Defined"})
    doc = lxml.html.fromstring(page.content)
    text = ""

    review_spans = doc.xpath(XPATH)
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

SEARCH_URL = "https://www.amazon.com/s?k="

class Navigator():
    def __init__(self, product_name):
        product_name = product_name.replace(' ', '+')
        url = SEARCH_URL + product_name
        page = requests.get(URL, headers={"User-Agent":"Defined"})
        print(page.content)
        self.html = lxml.html.fromstring(page.content)

    def get_products(self, n):
        """
        get the first n (or maximum) products in search results
        :param int n: The number of webpages to return
        :return: a list of webpages
        """
        pass

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
    nav = Navigator("miami memory")
    # TODO: write get_products