__author__ = 'Joe'
import argparse
import sys
sys.path.append("src/")
sys.path.append("src/res/")
import Crawler
import time

"""
Web fuzzer for SE331
"""

"""
Sets up the command line interface.
Defines arguments as per the readme
"""


def read_input():
    parser = argparse.ArgumentParser(usage="python fuzz.py [discover | test] url OPTIONS")
    parser.add_argument('mode', help="discover\n  Output a comprehensive, human readable " +
                                     "list of all discovered inputs to the system.\n" +
                                     "test\n      Discover all inputs, " +
                                     "then attempt a list of exploit vectors on those inputs. "+
                                     "Report vulnerabilities.", nargs=1)

    parser.add_argument('url', nargs=1, help="The URL to fuzz")
    parser.add_argument("--custom-auth=", help=
                        "Signal that the fuzzer should use hard-coded authentication " +
                        "for a specific application. Optional.", nargs='?', default='')

    parser.add_argument("--common-words=", help="Newline-delimited file of common words to be used " +
                        "in page guessing and input guessing. Required.", nargs='?')

    parser.add_argument("--vectors=", help="Newline-delimited file full of possible vulnerabilities",
                        nargs='?')

    parser.add_argument("--sensitive=", help="Newline-delimited file data that should never be leaked.",
                        nargs='?')

    parser.add_argument("--random=", action="store_true", help="When off, try each input systematically. " +
                        "When on, choose randomly.", default=False)

    parser.add_argument("--slow=", type=int, help="Number of ms considered to be slow.", nargs='?')
    return vars(parser.parse_args())

"""
Main method for execution.
"""


def main():

    args = read_input()
    crawl = Crawler.Crawler(args)
    start_time = time.time()
    crawl.crawl()
    output_string = "*****************\n" + "URLs and Forms Found \n*****************\n"
    for url in crawl.visited:
        output_string += "\nURL: " + url + "\n"
        if url in crawl.forms.keys():
            output_string += "Forms found on this page. Forms have fields: \n" + str(crawl.forms[url]) + "\n"
        else:
            output_string += "No form found on this page. \n"
    output_string += "\n*****************\n Cookies \n*****************\n"

    for key in crawl.cookies.keys():
        output_string += key + " : " + crawl.cookies[key] + "\n"

    with open("output.txt", "a+") as f:
        f.seek(0)
        f.truncate()
        f.write(output_string)
    print(output_string)
    print("Program runtime: " + str(time.time()-start_time) + "seconds")

main()