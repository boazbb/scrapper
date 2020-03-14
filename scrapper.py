import requests
import lxml
from lxml import html

URL = "https://www.amazon.com/Happy-Haystack-Stainless-Bottle-Design/product-reviews/B07YL48NZQ/&reviewerType=all_reviews"

r = requests.get(URL, headers={"User-Agent":"Defined"})
tree = lxml.html.fromstring(r.content)

hrefs = tree.xpath('//span[@class="review-text"]//a/@href')
print(hrefs)

# for element in tree.iter():
#     print("%s - %s" % (element.tag, element.text))