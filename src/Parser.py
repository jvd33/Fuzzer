from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin


"""
Custom HTML Parser to return interesting values from the HTML source.
"""


class Parser():

    def __init__(self):
        self.base_url = ''
        self.form_data = []
        self.found_urls = []
        self.urls = []
    """
    Finds all form input fields and all links in the HTML file.
    Adds them to the appropriate lists.
    """
    def parse(self, html, base_url):
        self.form_data = []
        parse_conf = SoupStrainer(['a', 'input'])
        soup = BeautifulSoup(html, "html.parser", parse_only=parse_conf)
        for element in soup.find_all('input'):
            if 'name' in element.attrs.keys():
                self.form_data.append(element.attrs['name'])


        for element in soup.find_all('a'): #for all <a> elements
            # if it contains 'href=', doesnt redirect, and hasn't been found yet
            if 'href' in element.attrs.keys() and element.attrs['href'].count('http') <= 1 \
                    and element.attrs['href'] not in self.urls and 'logout' not in element.attrs['href']:

                # add it to found, and then add it to urls to pass to crawler
                if 'http' not in element.attrs['href']:
                    self.found_urls.append(urljoin(base_url, element.attrs['href']))
                elif "127" in element.attrs['href']:
                    self.found_urls.append(element.attrs['href'])
                self.urls.append(element.attrs['href'])
