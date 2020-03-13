import requests
import lxml
from lxml import html

r = requests.get('http://gun.io')
tree = lxml.html.fromstring(r.content)
print('\n',tree.keys(),'\n')
elements = tree.get_element_by_id('class')
for el in elements:
    print(el.text_content())