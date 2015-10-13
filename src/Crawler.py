import requests
import re
import Parser
import random
from urllib.parse import urljoin, urlparse, parse_qs
import itertools


"""
Crawls the webpage, following links gathered from the parser and randomly generated links.
Handles login authentication, cookies, and forms as well.
"""


class Crawler:

    """
    Hard coded authentication information and file extensions for page guessing
    """
    dvwa = {'username': 'admin', 'password': 'password', 'Login': 'Login'}
    bodgeit = {'username': 'fake@fake.com', 'password1': 'password', 'password2': 'password'}
    extensions = ['.jsp', '.php', '.html', '.js', '.asp']

    """
    Constructor.
    Takes the args object returned by argsparser in Fuzz.read_input()
    For the arrays, opens the file and reads in the data. Splits it by \n
    mode = discover || test
    url = the URL to start fuzzing from
    authflag = custom authentication to DVWA or BodgeIt
    common = text file of common words for guessing
    vectors = text file of malicious input
    sensitive = text file of target sensitive data
    random = True/False
    slow = time that is considered "slow"
    accessible = list of accessible webpages
    visited = set (unique list) of visited urls
    forms = dictionary of form name and fields
    cookies = dictionary of cookie names and values
    """
    def __init__(self, args):
        self.mode = args['mode']
        self.url = args['url'][0]
        self.parser = Parser.Parser()
        self.authflag = args['custom_auth=']
        self.common = open('res/' + args['common_words='], 'r').read().split('\n')
        self.vectors = open('res/' + args['vectors='], 'r').read().split('\n') if args['vectors='] else []
        self.sensitive = open('res/'+args['sensitive='], 'r').read().split('\n') if args['sensitive='] else []
        self.random = args['random=']
        self.slow = args['slow=']
        self.accessible = []
        self.visited = set()
        self.forms = {}
        self.cookies = {}
        self.url_params = {}
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

    """
    Generates form data to post in an attempt to find vulnerabilities.
    n = number of fields found on the webpage to post to
    """
    def gen_form_data(self, n):
        pass


    """
    Posts to a form. For R2
    """
    def post_form(self, url, data, s):
        r = s.post(url, data=data, allow_redirects=True)
        return r

    """
    Generate random URLs to try to input, if the get request is successful, add the URL to the accessible list.
    """
    def find_random_urls(self, base_url, s):
        generated = []
        for word in self.common:
            extension = ''
            extension += word  # append the common word to the string
            for ext in self.extensions:
                extension += ext  # append the file extensions. eg "admin.jsp, admin.php..."
                url = urljoin(base_url, extension)  # completes the url by joining it with the base url.
                extension = word  # reset the word so we generate valid urls
                if s.get(url).status_code == requests.codes.ok:  # if the status code is ok then we can access the page.
                    generated.append(url)
        return generated

    """
    Gets the response of a given page
    """
    def get_response(self, url, s):
        r = s.get(url)
        return r

    def submit_form(self, form_data, s, url):
        if self.vectors:
            form_data = dict(itertools.compress(form_data, self.vectors))
        s.post(url, data=form_data, allow_redirects=True)

    """
    Crawls the webpage and finds all possible URLs to access
    returns the urls it successfully visited
    """
    def crawl(self):
        self.url = self.switch()
        # open a new session
        with requests.Session() as s:
            # get cookies and html from the initial page
            r = s.post(self.url, data=getattr(self, self.authflag), allow_redirects=True) if self.authflag \
                else s.get(self.url)
            html = r.text

            # if custom auth is on, go to the correct page
            if self.authflag == 'bodgeit':
                self.url = 'http://127.0.0.1:8080/bodgeit/'
            elif self.authflag == 'dvwa':
                s.cookies.pop('security')
                s.cookies['security'] = 'low'
                self.url = 'http://127.0.0.1/dvwa/'

            self.cookies.update(s.cookies.get_dict())
            self.visited.add(r.url)

            # parse the HTML from the new URL
            self.parser.parse(html, r.url)

            # update the forms
            if self.parser.form_data:
                self.forms.update({r.url: self.parser.form_data})

            # add any new urls that were found to the
            generated = self.find_random_urls(r.url, s)
            self.accessible.extend(generated)
            self.accessible.extend(self.parser.found_urls)

            for url in self.accessible:  # for all accessible urls, visit them and parse
                if url not in self.visited:
                    self.accessible.remove(url)
                    self.crawl_helper(url, s)

        return self.visited, self.parser.form_data

    """
    Helper function to visit each url
    Parses them and gets the links, form data, and cookies from the webpage.
    """
    def crawl_helper(self, url, s):
        html = self.get_response(url, s) if 'http:' in url else self.get_response(self.url + url, s)
        text = html.text
        parent_url = html.url
        self.parser.parse(text, parent_url)  # scan
        if self.parser.form_data:
            self.forms.update({url: self.parser.form_data})
        self.visited.add(url)
        self.accessible.extend([x for x in self.parser.found_urls if x not in self.visited])
        self.cookies.update(s.cookies.get_dict())
        self.url = url
        self.url_params.update({url: parse_qs(urlparse(url).query)})


