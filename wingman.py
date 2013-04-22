#!/usr/bin/env python
"""
wingman - driver program for goose python port
"""

__version__ = "1.00"
__author__ = "Robert Manson (robert@agogo.com)"

import sys
import optparse
import urllib
from goose.Goose import Goose
from goose.Configuration import Configuration


VERBOSE = False


def text_decode_helper(data, encoding):
    if encoding is None:
        detect = None
        try:
            from chardet import detect
            encoding = detect(data)['encoding']
        except ImportError:
            detect = lambda x: {'encoding': 'utf-8'}
            encoding = detect(data)['encoding']

    try:
        data = data.decode(encoding)
    except UnicodeDecodeError:
        data = data.decode("cp1252")
    return data


def read_file(file_, encoding):
    data = open(file_, 'rb').read()
    return text_decode_helper(data, encoding)

if __name__ == "__main__":
    p = optparse.OptionParser('%prog [(filename|url) [encoding]]',
                              version='%prog ' + __version__)
    p.add_option("-v", "--verbose", dest="verbose", action="store_true",
                 default=False, help="more descriptive output")

    (options, args) = p.parse_args()

    if options.verbose:
        VERBOSE = True

    # process input
    if len(args) > 0:
        file_ = args[0]
        encoding = None
        if len(args) == 2:
            encoding = args[1]
        if len(args) > 2:
            p.error('Too many arguments')

        if file_.startswith('http://') or file_.startswith('https://'):
            baseurl = file_
            j = urllib.urlopen(baseurl)
            text = j.read()
            if encoding is None:
                try:
                    from feedparser import _getCharacterEncoding as enc
                    encoding = enc(j.headers, text)[0]
                except ImportError:
                    enc = lambda x, y: ('utf-8', 1)
                    encoding = enc(j.headers, text)[0]
                if encoding == 'us-ascii':
                    encoding = 'utf-8'
            data = text_decode_helper(text, encoding)

        else:
            data = read_file(file_, encoding)
    else:
        data = sys.stdin.read()

    config = Configuration()
    config.enableImageFetching = False

    g = Goose(config=config)

    article = g.extractContent(url='http://www.apple.com', rawHTML=data)

    sys.stdout.write("Title: ")
    print article.title
    sys.stdout.write("Publish Date: ")
    print article.publishDate

    sys.stdout.write("Tags: ")
    tags = list(article.tags)
    print tags
    sys.stdout.write("meta-keywords: ")
    print article.metaKeywords
    sys.stdout.write("meta-description: ")
    print article.metaDescription
    sys.stdout.write("Article Text: ")
    print article.cleanedArticleText
