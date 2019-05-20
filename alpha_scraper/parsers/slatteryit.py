from __future__ import print_function

import calendar
from datetime import datetime
from itertools import chain, ifilterfalse
from operator import itemgetter
from platform import python_version_tuple

import nltk
from bs4 import BeautifulSoup
from six import iteritems

if python_version_tuple()[0] == '3':

    imap = map
    ifilter = filter

else:
    from itertools import imap, ifilter


########
# Root #
########

def parse_title_to_epoch(title):
    """
    :param title:
    :type title: unicode
    :return: time since epoch
    :rtype int
    """
    # E.g.: "Slattery's  Watch - 10 November 2014"
    title = title.encode('ascii', errors='ignore')
    if not title[-1].isdigit():
        title = '{title} {year:d}'.format(title=title, year=datetime.now().year)
    title = title[title.rfind('-') + 1:].lstrip()
    if title == 'The Watch 2018':
        return None
    try:
        return calendar.timegm(datetime.strptime(title, '%A %d %B %Y' if len(title) > 18 else '%d %B %Y').timetuple())
    except ValueError:
        return None


def parsed_the_watch_archive(response):
    soup = response if isinstance(response, BeautifulSoup) else BeautifulSoup(response.body, 'html.parser')
    return tuple(imap(itemgetter(1), sorted(chain.from_iterable(
        imap(lambda div: tuple(ifilter(
            lambda title_href: title_href[0] is not None,
            imap(lambda ahref: (parse_title_to_epoch(ahref.get('title')), ahref.get('href')), div.find_all('a'))
        )), soup.findAll('div', {'class': 'campaign'})))
        , key=itemgetter(0))))


#######################
# Newsletter campaign #
#######################

def get_date_name(response):
    soup = response if isinstance(response, BeautifulSoup) else BeautifulSoup(response.body, 'html.parser')
    title = soup.title.string.encode('ascii', errors='ignore')
    return title[title.rfind('-') + 2:].rstrip().replace(' ', '_')


def _get_named_entities(sentence):
    return ((chunk.label(), ' '.join(c[0] for c in chunk))
            for sent in nltk.sent_tokenize(sentence)
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
            if hasattr(chunk, 'label'))


newsletter_stop_words = frozenset(('email', 'subscribe', 'contact', 'privacy', 'print'))
stemmer = nltk.stem.snowball.SnowballStemmer('english')
lemmer = nltk.stem.WordNetLemmatizer()


def parsed_campaign(response):
    soup = response if isinstance(response, BeautifulSoup) else BeautifulSoup(response.body, 'html.parser')
    # print(soup.prettify(encoding='utf8'))
    return {get_date_name(soup): tuple(
        ifilter(None, imap(lambda td: {k: v for k, v in iteritems({
            'urls': dict(
                ifilterfalse(
                    lambda tup: any(ifilter(lambda word: any(
                        (lambda word: ifilter(lambda stop_word: stop_word in word, newsletter_stop_words)
                         )(lemmer.lemmatize(word.lower()))),
                                            nltk.word_tokenize(tup[0]))),
                    imap(lambda ahref: (ahref.text.strip(), ahref.get('href')),
                         td.findAll('a'))
                )
            ),
            'named_entities': tuple(ifilter(None, _get_named_entities(td.text.strip())))}) if v},
                           soup.findAll('td', {'class': 'mcnTextContent'}))))
    }
