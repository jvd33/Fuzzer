__author__ = 'joe'
from html.parser import HTMLParser


class Parser(HTMLParser):

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.base_url = ''
        self.form_data = {}
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'form':
            coll = dict(attrs)
            for key, val in coll.items():
                if val == 'hidden':
                    coll.pop(key)
            self.form_data.update(coll)
        if tag == 'a':
            coll = dict(attrs)
            for key, val in coll.items():
                if key == 'href' and 'hiderefer' not in coll[key] and 'logout' not in coll[key]:
                    self.urls.append(coll[key])



    def get_urls(self):
        return self.urls


    def get_form_data(self):
        return self.form_data

