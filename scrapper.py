import requests
import lxml
from lxml import html
from tqdm import tqdm # for pretty progress bars
import argparse
import json
import time

SEARCH_URL = "https://www.amazon.com/s?k={SEARCH_TERM}&page={PAGE_NUM}"
CAT_SEARCH_URL = "https://www.amazon.com/s?k={SEARCH_TERM}&i={CATEGORY}&page={PAGE_NUM}"
AMAZON_PREFIX = "https://www.amazon.com"

PRODUCT_XPATH = '//a[@class="a-link-normal a-text-normal"]'
REVIEW_BUTTON_XPATH = '//a[@class="a-link-emphasis a-text-bold"]'
#REVIEW_COUNT_XPATH = '//span[@data-hook="cr-filter-info-review-count"]'
REVIEW_COUNT_XPATH = '//span[@class="a-size-base a-color-secondary"]'
REVIEW_COUNT_XPATH_ALT = '//span[@data-hook="cr-filter-info-review-rating-count"]'
REVIEW_TEXT_XPATH = '//span[@class="a-size-base review-text review-text-content"]'
BULLET_XPATH = '//span[@class="a-list-item"]'
PRODUCT_DESCRIPTION_XPATH = '//div[@id="productDescription"]'

# The browser we pretend to be:
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
            #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        }

# hpc is health and household. just add &i={} in the url
categories = ["arts-crafts", "automotive", "baby-products", "beauty", "stripbooks", "computers", "digital-music", "electronics", "digital-text",
                "instant-video", "fashion-womens", "fashion-mens", "fashion-girls", "fashion-boys", "deals", "hpc", "kitchen", "industrial", 
                "luggage", "movies-tv", "music", "pets", "software", "sporting", "tools", "toys-and-games", "videogames"]

# Number of reviews in a single page
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
    json_dict = {}
    for prod in products:
        prod_info_dict = nav.get_product_info_dict(AMAZON_PREFIX+prod.url)
        print(f'prod url is {prod.url}')
        rev_url = prod.url.replace("/dp/", "/product-review/").replace("/gp/", "/product-review/")
        reviews = nav.get_product_review_text(AMAZON_PREFIX+rev_url)
        json_dict[rev_url] = {'Product Info': prod_info_dict, 'Reviews': reviews}
    with open(args.json_path, 'w') as save_file:
        save_file.write(json.dumps(json_dict))

"""
A class that represents a product, containing the URL of the product
and the texts of the reviews
"""
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


"""
A class that navigates through amazon, looking for the review texts of all
the product in the search
"""
class Navigator():
    def __init__(self, search_term, category=None, max_review_pages=None):
        self.search_term = search_term.replace(' ', '+')
        self.category = category
        if category and category not in categories:
            print("Wrong category, doing general search instead.")
            self.category = None
        self.max_review_pages = max_review_pages

    def get_url(self, page_num):
        """
        Gets the URL of one of the pages in the results 
        """
        if self.category:
            return CAT_SEARCH_URL.format(SEARCH_TERM=self.search_term, CATEGORY=self.category, PAGE_NUM=page_num)
        else:
            return SEARCH_URL.format(SEARCH_TERM=self.search_term, PAGE_NUM=page_num)

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
            page = requests.get(url, headers=headers)
            self.doc = lxml.html.fromstring(page.content)
            products_a = self.doc.xpath(PRODUCT_XPATH)
            if (len(products_a) == 0):
                # This means we reached a page without products
                break 
            for p in products_a:
                if len(products_urls) > n: break # If we already have n products we can return
                # For some reason we get duplicates sometime, also another search result k=SEARCHTERM
                if not (p.get('href') in products_urls) and not p.get('href').startswith('/s?k='):
                    products_urls.append(p.get('href'))
            i += 1
        print(f"Found {len(products_urls)} items.")
        print(f"\nProduct URLs:\n{products_urls}\n")
        return Product.url_list_to_product_list(products_urls)

    def get_all_reviews_from_page(self, url):
        """
        Extracts all the reviews from the given URL
        :param url: The url of the page with the reviews
        :return: A string with all the reviews in the page
        """
        page = requests.get(url, headers=headers)
        doc = lxml.html.fromstring(page.content)
        text = ""

        review_spans = doc.xpath(REVIEW_TEXT_XPATH)
        for rev in review_spans:
            for i in rev:
                text += str(i.text) + " "
        # Encoding into UTF8 to make sure no bas characters are in the string
        return text.encode('utf8',errors='ignore').decode()

    def get_product_review_text(self, product_webpage):
        """
        :param product_webpage: The URL of the product itself
        :return: a list of URLs of the product's review pages
        """
        # Find the overall number of reviews:
        # Amazon is blocking the connection so im trying a sleep:
        time.sleep(5)
        page = requests.get(product_webpage, headers=headers)
        doc = lxml.html.fromstring(page.content)
        if 'To discuss automated access to Amazon data please contact' in page.content.decode():
            print(f'\nCould not access review page for product at: {product_webpage}\nAmazon blocked the access due to automation.\n')
            return []
        print(doc)
        try:
            print(f"Text is {doc.xpath(REVIEW_COUNT_XPATH)[0].text}")
            count = int(doc.xpath(REVIEW_COUNT_XPATH)[0].text.split()[0].replace(',',''))
            print(f"Count is {count}")
        except IndexError:
            print(f"\nError in parsing review data")
            print(doc.xpath(REVIEW_COUNT_XPATH), '\n')
            return []
        page_number = - (-count // REVIEW_IN_PAGE) # Rounding Up
        if self.max_review_pages:
            page_number = min(page_number, self.max_review_pages)
        page_suffix = "&pageNumber={num}"
        text_list = []
        print(f"\nScanning review pages for product {product_webpage.split('/')[3]}")
        for i in tqdm(range(1, page_number+1)):
        # Get the review text:
            text_list.append(self.get_all_reviews_from_page(product_webpage+page_suffix.format(num=i)))
        return text_list

    def get_product_info_dict(self, product_webpage):
        """
        Gets the product information
        :param product_webpage: The main URL for the product
        :return: A dictionary with 2 keys: 'Bullets' for the list of short descriptions,
        and 'Product Description' for the long paragraph. Not all products have both.
        """
        # Get information bullets:
        page = requests.get(product_webpage, headers=headers)
        doc = lxml.html.fromstring(page.content)
        divs = doc.xpath(BULLET_XPATH)
        bullets = []
        for i in divs:
            if (i.text):
                if (i.text.strip()):
                    bullets.append(i.text.strip().encode('utf8',errors='ignore').decode())
        # get procuct description
        desc = ''
        prod_desc = doc.xpath(PRODUCT_DESCRIPTION_XPATH)
        if len(prod_desc) > 0:
            prod_desc = prod_desc[0]
            if len(prod_desc) == 3:
                if not prod_desc[2].text:
                    desc = ""
                else:
                    desc = prod_desc[2].text.encode('utf8',errors='ignore').decode()
        return {'Bullets': bullets, 'Product Description': desc}

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
        '-j', '--json-path',
        help='The path to save the JSON to',
        metavar="json_path", default="scrapper_results.json"
        )
    parser.add_argument(
        '-rp', '--review-pages',
        help='Maximum number of review pages to search for in every product', type=int
        )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()