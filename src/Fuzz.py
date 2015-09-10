__author__ = 'Joe'
import sys
import argparse

"""
Web fuzzer for SE331
"""


def read_input():
    parser = argparse.ArgumentParser(usage="python fuzz.py [discover | test] url OPTIONS")
    parser.add_argument('mode', help="COMMANDS:\n  discover  Output a comprehensive, human readable " +
                                     "list of all discovered inputs to the system.\n" +
                                     "  test      Discover all inputs, " +
                                     "then attempt a list of exploit vectors on those inputs. "+
                                     "Report vulnerabilities.", nargs=1)

    parser.add_argument('url', nargs=1)
    parser.add_argument("--custom-auth=", help=
                        "Signal that the fuzzer should use hard-coded authentication " +
                        "for a specific application. Optional.", nargs='?')
    parser.add_argument("--common-words=", help="Newline-demilited file of common words to be used " +
                                                "in page guessing and input guessing. Required.", nargs='?')
    parser.add_argument("--vectors=", help="Newline-demilited file data that should never be leaked.",
                        nargs='?')
    parser.add_argument("--sensitive=", help="Newline-demilited file data that should never be leaked.",
                        nargs='?')

def main():
    sensitive = []
    common = []
    vectors = []
    random = False
    auth = ''
    read_input(sys.argv)