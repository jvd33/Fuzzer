__author__ = 'Joe'
from requests.auth import HTTPBasicAuth
import requests
import re
import Parser


"""
Class representing a single new page that was discovered by the crawler
children - a list of all pages that were found from the current page
url - current url
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
        self.parser = Parser.Parser(self.url)
        self.authflag = args['custom_auth=']
        self.common = open('res/' + args['common_words='], 'r').read().split('\n') if args['common_words='] else []
        self.vectors = open('res/' + args['vectors='], 'r').read().split('\n') if args['vectors='] else []
        self.sensitive = open('res/'+args['sensitive='], 'r').read().split('\n') if args['sensitive='] else []
        self.random = args['random=']
        self.slow = args['slow=']
        self.accessible = []
        self.visited = []


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
            '': 'http://127.0.0.1'
        }[self.authflag]


    """
    Logs in with the custom credentials, otherwise starts at localhost

    def open_connection(self):
        url = self.switch()
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth('admin', 'password')
        r = self.session.post(url, allow_redirects=True)
        html = self.get_html(r.url)
        self.parse_urls(html)
    """
    def parse_forms(self, html):
        pass

    """
    Returns a list of all urls found on the HTML page
    """
    def parse_urls(self, html, s):
        self.url = 'http://127.0.0.1:8080/bodgeit/' if self.authflag == 'bodgeit' else 'http://127.0.0.1/dvwa/'
        for url in re.findall('<a href="?\'?([^"\'>]*)', html):
            if link + url not in self.accessible and "logout" not in url and "hiderefer" not in url:
                self.accessible.append(link + url)


    def post_form(self, url, data, s):
        r = s.post(url, data=data, allow_redirects=True)
        return r



    """
    Gets the pure HTML of a given page
    """
    def get_html(self, url, s):
        r = s.get(url)
        return r.text if r.status_code == requests.codes.ok else ''


    """
    Crawls the webpage and finds all possible URLs to access
    returns the urls it successfully visited
    """
    def crawl(self):
        url = self.switch()
        with requests.Session() as s:
            r = s.post(url, data=getattr(self, self.authflag), allow_redirects=True)
            html = self.get_html(r.url, s)
            self.url = 'http://127.0.0.1:8080/bodgeit/' if self.authflag == 'bodgeit' else 'http://127.0.0.1/dvwa/'
            self.parser.feed(html)
            self.accessible.extend(self.parser.get_urls())
            #self.parse_urls(html, s)
            for url in self.accessible:
                self.crawl_helper(url, s)
        return self.visited


    """
    Helper function to make visit each url
    """
    def crawl_helper(self, url, s):
        html = self.get_html(self.url+url, s)
        self.parser.feed(html)
        if url not in self.visited:
            self.visited.append(url)
        for url in self.parser.get_urls():
            if url not in self.accessible:
                self.accessible.extend(self.parser.get_urls())
                
