__author__ = 'Joe'
import requests

"""
Class representing a single new page that was discovered by the crawler
children - a list of all pages that were found from the current page
url - current url
"""


class URL:


    def __init__(self, url):
        self.url = url
        self.visited = []
        self.children = []

    """
    Adds a child to the list if it has not been visited yet.
    """
    def add_child(self, url):
        if not url in self.visited:
            self.children.append(url)


    def crawl(self):
