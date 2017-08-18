import time
import socket
import multiprocessing
import logging
import requests

WEBSITE_LIST = [
    'http://envato.com',
    'http://amazon.co.uk',
    'http://amazon.com',
    'http://facebook.com',
    'http://google.com',
    'http://google.fr',
    'http://google.es',
    'http://google.co.uk',
    'http://internet.org',
    'http://gmail.com',
    # 'http://stackoverflow.com',
    # 'http://github.com',
    # 'http://heroku.com',
    # 'http://really-cool-available-domain.com',
    # 'http://djangoproject.com',
    # 'http://rubyonrails.org',
    # 'http://basecamp.com',
    # 'http://trello.com',
    # 'http://yiiframework.com',
    # 'http://shopify.com',
    # 'http://another-really-interesting-domain.co',
    # 'http://airbnb.com',
    # 'http://instagram.com',
    # 'http://snapchat.com',
    # 'http://youtube.com',
    # 'http://baidu.com',
    # 'http://yahoo.com',
    # 'http://live.com',
    # 'http://linkedin.com',
    # 'http://yandex.ru',
    # 'http://netflix.com',
    # 'http://wordpress.com',
    # 'http://bing.com',
]
 
class WebsiteDownException(Exception):
    pass
 
def ping_website(address, timeout=20):
    """
    Check if a website is down. A website is considered down 
    if either the status_code >= 400 or if the timeout expires
     
    Throw a WebsiteDownException if any of the website down conditions are met
    """
    try:
        response = requests.head(address, timeout=timeout)
        if response.status_code >= 400:
            logging.warning("Website %s returned status_code=%s" % (address, response.status_code))
            raise WebsiteDownException()
        else:
            return 'success'
    except requests.exceptions.RequestException:
        logging.warning("Timeout expired for website %s" % address)
        raise WebsiteDownException()
 
def notify_owner(address):
    """ 
    Send the owner of the address a notification that their website is down 
     
    For now, we're just going to sleep for 0.5 seconds but this is where 
    you would send an email, push notification or text-message
    """
    logging.info("Notifying the owner of %s website" % address)
    time.sleep(0.5)
     
def check_website(address):
    """
    Utility function: check if a website is down, if so, notify the user
    """
    time.sleep(2)
    try:
        print("pinging",address)
        return ping_website(address)
    except WebsiteDownException:
        notify_owner(address)

NUM_WORKERS = len(WEBSITE_LIST)
# NUM_WORKERS = 4
# NUM_WORKERS = 1
 
start_time = time.time()
 
with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
    results = pool.map_async(check_website, WEBSITE_LIST)
    results.wait()
    print(results.get())
 
end_time = time.time()        
 
print("Time for MultiProcessingSquirrel: %ssecs" % (end_time - start_time))
 
# WARNING:root:Timeout expired for website http://really-cool-available-domain.com
# WARNING:root:Timeout expired for website http://another-really-interesting-domain.co
# WARNING:root:Website http://bing.com returned status_code=405
# Time for MultiProcessingSquirrel: 2.8224599361419678secs
