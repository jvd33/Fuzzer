__author__ = 'joe'
from html.parser import HTMLParser


class Parser(HTMLParser):

    def __init__(self, url):
        self.base_url = ''
        self.form_data = {}
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'form':
            for key, val in attrs:
                if key == 'hidden':
                    attrs.pop(key, val)
            self.form_data.update({attrs})
        if tag == 'a' and 'logout' not in attrs['href'] and 'hiderefer' not in attrs['href']:
            self.urls.append(attrs['href'])



    def get_urls(self):
        return self.urls


    def get_form_data(self):
        return self.form_data

