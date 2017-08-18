import feedparser

import feeds

import copy
import re
import html
import time
import logging
import multiprocessing
from threading import Thread
from queue import Queue

logging.basicConfig(level=logging.DEBUG)

q = Queue()

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
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.data = None
        self.last_parsed = None

    def __repr__(self):
        return "key {}, url {}, #stories {}".format(self.key, self.url, len(self.data['entries']))

class RSSFeedManager(object):
    def __init__(self, feed_list, update_interval, num_processes):
        self.feeds = {}
        self.update_interval = update_interval
        for feed in feed_list:
            self.add_feed(**feed)
        self.num_processes = num_processes
        self.update_thread = None
        self.test_state = []

    def add_feed(self, url, key=None):
        if key is None:
            key = url
            logging.info("Adding feed {} to update every {} seconds".format(url, key, self.update_interval))
        logging.info("Adding feed {} with key {} to update every {} seconds".format(url, key, self.update_interval))
        self.feeds[key] = RSSFeed(url, key)

    def download_feed(self, feed):
        '''
        :param feed: an RSSFeed type object
        '''
        logging.info("Downloading feed {}".format(feed.key))
        feed.data = feedparser.parse(feed.url)
        return feed
    
    # run feed updater on its own thread
    def get_feeds(self):
        global q
        # add means to terminate updating.
        while True:
            logging.info("Updating feeds, update interval {}".format(self.update_interval))
            out = None
            with multiprocessing.Pool(processes=self.num_processes) as pool:
                results = pool.map_async(self.download_feed, list(self.feeds.values()))
                results.wait()
                out = results.get() # array of feed objects
                for result in out:
                    logging.info('Got result {}'.format(result))
            q.put(out)
            time.sleep(self.update_interval)

    def echo_results(self):
        global q
        while True:
            self.test_state.append(q.get())
            time.sleep(2)
            logging.info('STATE CHECK {}, Queue State {}'.format(len(self.test_state), q.empty()))
            time.sleep(3)

if __name__ == "__main__":
    r = RSSFeedManager(feed_list=feeds.feed_list, update_interval=3, num_processes=4)
    t = Thread(target=r.get_feeds, args=())
    t.start()
    t2 = Thread(target=r.echo_results, args=())
    t2.start()

    time.sleep(10)
    print("OUTSIDE SHIT!", r.test_state)
