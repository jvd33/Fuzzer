import requests
from datetime import timedelta
import Parser
import random
from urllib.parse import urljoin, urlparse, parse_qs



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
        self.slow = timedelta(milliseconds=args['slow='])
        self.accessible = []
        self.visited = set()
        self.forms = {}
        self.cookies = {}
        self.session = None
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
            self.session = s
            self.cookies.update(s.cookies.get_dict())
            self.visited.add(r.url)

            # parse the HTML from the new URL
            self.parser.parse(html, r.url)

            # update the forms
            if self.parser.form_data:
                self.forms.update({r.url: self.parser.form_data})

            # add any new urls that were found to the list
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
        html = s.get(url) if 'http:' in url else s.get(self.url + url)
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

    """
    Submits vectors to forms and logs behavior.
    Submits to all forms on each webpage that has forms
    """
    def test(self):
        self.crawl()
        output = set()
        with self.session as s:
            if self.random:
                random.seed()
                while self.visited:
                    target = self.visited.pop()
                    data = {}
                    if target in self.forms.keys() and 'login' not in target:
                        for key in self.forms[target]:
                            vector = self.vectors[random.randint(0, len(self.vectors))]
                            data.update({key: vector})
                            response = s.post(target, data=data, allow_redirects=True)
                            temp = self.check_response(response, vector)
                            if temp not in output:
                                output.add(temp)

            else:
                for url in self.visited:
                    data = {}
                    if url in self.forms.keys() and 'login' not in url:
                        for key in self.forms[url]:
                            for vector in self.vectors:
                                if key == "Submit" or key == "submit":
                                    data.update({key: "Submit"})
                                else:
                                    data.update({key: vector})

                                response = s.post(url, data=data, allow_redirects=True)
                                temp = self.check_response(response, vector)
                                if temp not in output:
                                    output.add(temp)

            return output

    """
    Check the response of each sent vector.
    """
    def check_response(self, r, v):
        output = ""
        sanitized = ["<", ">", "/", "\\", "'"]

        if r.status_code != requests.codes.ok:  # bad response exploit check
            output += "\nPosting to " + r.url + " with vector " + v + \
                      " returns invalid response " + self.http_codes(r.status_code) + "\n"

        if r.elapsed > self.slow:  # slow response exploit check
            output += "\nResponse time for post to " + r.url + " was slow with vector " + v + "\n"

        for sens in self.sensitive:  # sensitive data exploit check
            if sens in r.text:
                output += "\nSensitive data leaked from " + r.url + " " + sens + " found.\n"

        for char in sanitized:  # input sanitization check
            if char in v:
                if v in r.text:
                    output += "\nPossible lack of sanitation on " + r.url + ", vector " + v + " not sanitized.\n"

        return output

    """
    human-readable http codes
    """
    def http_codes(self, code):
        return {
            500: '500, internal server error encountered',
            400 : '400, bad request sent.',
            403 : '403, page access is forbidden.'
        }.get(code)