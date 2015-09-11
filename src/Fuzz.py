__author__ = 'Joe'
import argparse
import sys
sys.path.append("src/")
sys.path.append("src/res/")
import Crawler


"""
Web fuzzer for SE331
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

def main():

    args = read_input()
    crawl = Crawler.Crawler(args)
    crawl.open_connection()
    crawl.crawl()
    for url in crawl.visited:
        print(url + '\n')

main()