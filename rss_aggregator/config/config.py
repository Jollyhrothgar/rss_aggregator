import os
import logging
import logging.config
import json

config_dir = os.path.split(__file__)[0]
feed_list_file = os.path.join(config_dir,'feeds.json')
update_interval = 30 # seconds
log_config = os.path.join(config_dir,'logging.conf')

if __name__ == '__main__':
    logger = logging.getLogger("rss_aggregator.config_test")
    logger.info("Loaded Feed List, {} feeds".format(len(feed_list)))
    logger.info("Update Interval {}".format(update_interval))
    logger.info("Logging Config {}".format(log_config))
