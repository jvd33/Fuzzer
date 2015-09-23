__author__ = 'Joe'
from requests.auth import HTTPBasicAuth
import requests
import re
import Parser
import random
import itertools


"""
Crawls the webpage, following links gathered from the parser and randomly generated links.
Handles login authentication, cookies, and forms as well.
"""
class Crawler:

    dvwa = {'username': 'admin', 'password': 'password', 'Login': 'Login'}
    bodgeit = {'username': 'fake@fake.com', 'password1': 'password', 'password2': 'password'}
    extensions = ['.jsp', '.php', '.html', '.js', '.asp']

    """
    Constructor.
    Takes the args object returned by argsparser in Fuzz.read_input()
    For the arrays, opens the file and reads in the data. Splits it by \n
    """
    def __init__(self, args):
        self.mode = args['mode']
        self.url = args['url'][0]
        self.parser = Parser.Parser()
        self.authflag = args['custom_auth=']
        self.common = open('res/' + args['common_words='], 'r').read().split('\n') if args['common_words='] else []
        self.vectors = open('res/' + args['vectors='], 'r').read().split('\n') if args['vectors='] else []
        self.sensitive = open('res/'+args['sensitive='], 'r').read().split('\n') if args['sensitive='] else []
        self.random = args['random=']
        self.slow = args['slow=']
        self.accessible = []
        self.visited = set()
        self.forms = {}
        self.cookies = {}

    """
    String representation of a Crawler for debugging.
    """
    def __str__(self):
        return "[" + self.mode[0] + ", " + self.url[0] + ", " + self.authflag + "]"

    """
    Acts as a switch/case.
    Provides the proper URL for the auth flag, if given.
    Otherwise starts from home
    """
    def switch(self):
        return {
            'dvwa': 'http://127.0.0.1/dvwa/login.php',
            'bodgeit': 'http://127.0.0.1:8080/bodgeit/register.jsp',
            '': 'http://127.0.0.1/'
        }[self.authflag]


    def post_form(self, url, data, s):
        r = s.post(url, data=data, allow_redirects=True)
        return r

    """
    Used to discover potentially unlinked pages.
    """
    def post_url(self,url,s):
        print(self.common)
        r = s.post(url,self.common[0],allow_redirects=True)
        return r

    """
    Gets the pure HTML of a given page
    """
    def get_html(self, url, s):
        r = s.get(url)
        return r

    def submit_form(self, form_data, s, url):
        form_names = form_data
        if self.vectors:
            form_data = dict(itertools.compress(form_data, self.vectors))
        r = s.post(url, data=form_data, allow_redirects=True)

    """
    Crawls the webpage and finds all possible URLs to access
    returns the urls it successfully visited
    """
    def crawl(self):
        self.url = self.switch()
        with requests.Session() as s:
            r = s.post(self.url, data=getattr(self, self.authflag), allow_redirects=True) if self.authflag \
                else s.get(self.url)
            html = r.text
            self.cookies.update(s.cookies.get_dict())

            if self.authflag == 'bodgeit':
                self.url = 'http://127.0.0.1:8080/bodgeit/'
            elif self.authflag == 'dvwa':
                self.url = 'http://127.0.0.1/dvwa/'

            self.visited.add(r.url)
            self.parser.parse(html, r.url)

            if self.parser.form_data:
                self.forms.update({r.url: self.parser.form_data})

            self.accessible.extend(self.parser.found_urls)

            for url in self.accessible:
                if url not in self.visited:
                    self.accessible.remove(url)
                    self.crawl_helper(url, s)

        return self.visited, self.parser.form_data

    """
    Helper function to visit each url
    """
    def crawl_helper(self, url, s):
        html = self.get_html(url, s) if 'http:' in url else self.get_html(self.url + url, s)
        text = html.text
        parent_url = html.url
        self.parser.parse(text, parent_url)
        if self.parser.form_data:
            self.forms.update({url: self.parser.form_data})
        self.visited.add(url)
        self.accessible.extend([x for x in self.parser.found_urls if x not in self.visited])
        self.cookies.update(s.cookies.get_dict())
        self.url = url
