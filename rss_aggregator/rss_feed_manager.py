import feedparser
import requests

from io import BytesIO
import json
import copy
import re
import html
import time
import logging
import multiprocessing
from threading import Thread
from queue import Queue

## TODO
# 1. Multithreading - Everything writes to the queue
# 2. Separate thread reads from queue and updates a database

logging.basicConfig(level=logging.DEBUG)
news_queue = multiprocessing.Queue() # must be multiprocessing queue to share
                                     # queue across processes
control_queue = Queue()

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
        self.message = None

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
            logging.info("RSSFeedManager.add_feed: key:{}, url:{}, update_interval:{}".format(url, key, self.update_interval))
        logging.info("RSSFeedManager.add_feed: key:{}, url:{}, update_interval:{}".format(url, key, self.update_interval))
        self.feeds[key] = RSSFeed(url, key)
        return

    def download_feed(self, feed):
        '''
        :param feed: an RSSFeed type object
        :param news_queue: put news on the queue for processing
        '''
        global news_queue

        try:
            resp = requests.get(feed.url, timeout=20.0) 
        except requests.ReadTimeout:
            logging.warn("RSSFeedManager.download_feed: timeout, key:{}".format(feed.key))
            return
        content = BytesIO(resp.content)
        feed.data=feedparser.parse(content)
        feed.message="SUCCESS"
        logging.info("RSSFeedManager.download_feed: stories:{}, key:{}".format(len(feed.data['entries']), feed.key))
        news_queue.put(feed)
    
    # run feed updater on its own thread
    def get_feeds(self):
        # add means to terminate updating.
        global news_queue
        while True:
            logging.info("RSSFeedManager.get_feeds updating".format(self.update_interval))
            with multiprocessing.Pool(processes=self.num_processes) as pool:
                results = pool.map_async(self.download_feed, list(self.feeds.values()))
                results.wait()
            logging.info("RSSFeedManager.get_feeds sleeping")
            time.sleep(self.update_interval)

    def echo_results(self):
        global news_queue

        while True:
            data = news_queue.get()
            logging.info('GOT {}'.format(data))
            self.test_state.append(data)
            logging.info('RSSFeedManager.echo_results, test_state:{}, news_queue.empty():{}'.format(len(self.test_state), news_queue.empty()))

if __name__ == "__main__":
    with open('feeds.json','r') as f:
        feeds = json.load(f)

    r = RSSFeedManager(feed_list=feeds, update_interval=30, num_processes=4)
    t = Thread(target=r.get_feeds, args=())
    t.start()

    t2 = Thread(target=r.echo_results, args=())
    t2.start()
