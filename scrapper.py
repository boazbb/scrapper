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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }

# hpc is health and household. just add &i={} in the url
categories = ["arts-crafts", "automotive", "baby-products", "beauty", "stripbooks", "computers", "digital-music", "electronics", "digital-text",
                "instant-video", "fashion-womens", "fashion-mens", "fashion-girls", "fashion-boys", "deals", "hpc", "kitchen", "industrial", 
                "luggage", "movies-tv", "music", "pets", "software", "sporting", "tools", "toys-and-games", "videogames"]


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
            page = requests.get(url, headers=headers)
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
        page_suffix = "&pageNumber={num}"
        text = self.get_all_reviews_from_page(product_webpage)
        i = 2
        new_text = self.get_all_reviews_from_page(product_webpage+page_suffix.format(num=i))
        while(new_text != ""):
            print(f"i is {i}")
            text += new_text
            i += 1
            new_text = self.get_all_reviews_from_page(product_webpage+page_suffix.format(num=i))
        return text


if __name__ == "__main__":
    nav = Navigator("table")
    products_urls = nav.get_products(1)
    all_review = ""
    for prod_url in tqdm(products_urls):
        rev_url = prod_url.replace("/dp/", "/product-review/")
        all_review += (" "+nav.get_product_review_text(AMAZON_PREFIX+rev_url))
    adj_dict = text_to_adj_dict(all_review)
    print(adj_dict)


#TODO: Think of a better structure
#TODO: Add Product Information Text w. different dictionaries
#TODO: And Spacy/or better nltk
#TODO: Saving the url of the products, with a dict per URL
#TODO: Adding search by category
#TODO: In the dictionary, save a pointer to the original text
#TODO: Add option to export (use argparser)