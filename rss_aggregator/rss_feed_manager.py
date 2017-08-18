import feedparser

import feeds

import copy
import re
import html
import time
import logging
import multiprocessing

logging.basicConfig(level=logging.DEBUG)

def santize_html(s):
    """Take an input string s, find all things that look like SGML character
    entities, and replace them with the Unicode equivalent.
    Function is from:
    
    http://stackoverflow.com/questions/1197981/convert-html-entities-to-ascii-in-python/1582036#1582036
    """
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass
    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if name in html.entities.name2codepoint:
            s = s.replace(hit,
                          unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s

class RSSFeed(object):
    def __init__(self, url, key, update_interval):
        self.url = url
        self.key = key
        self.update_interval = update_interval
        self.data = None
        self.last_parsed = None

class RSSFeedManager(object):
    def __init__(self, feed_list):
        self.feeds = {}
        for feed in feed_list:
            self.add_feed(**feed)

    def add_feed(self, url, key=None, update_interval=60):
        if key is None:
            key = url
            logging.info("Adding feed {} to update every {} seconds".format(url, key, update_interval))
        logging.info("Adding feed {} with key {} to update every {} seconds".format(url, key, update_interval))
        self.feeds[key] = RSSFeed(url, key, update_interval)

    def download_one_feed(self, feed):
        '''
        :param feed: an RSSFeed type object
        '''
        logging.info("Downloading feed {}".format(feed.key))
        time.sleep(feed.update_interval)
        return 'content'

    def download_rss(self, num_processes):
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map_async(self.download_one_feed, list(self.feeds.values()))
            results.wait()
            print(results.get())

if __name__ == "__main__":
    r = RSSFeedManager(feeds.feed_list)
    r.download_rss(num_processes=5)
