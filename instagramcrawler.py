import argparse
import os
import re
import sys
import time
from urlparse import urljoin

import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# HOST
HOST = 'http://www.instagram.com'

# SELENIUM CSS SELECTOR
CSS_LOAD_MORE = "a._8imhp._glz1g"

# JAVASCRIPT COMMANDS
SCROLL_UP = "window.scrollTo(0, 0);"
SCROLL_DOWN = "window.scrollTo(0, document.body.scrollHeight);"

class InstagramCrawler(object):
    def __init__(self):
        self._driver = webdriver.Firefox()

        self.data = {}

    def crawl(self, query, number, caption, dir_prefix):
        print("Query: {}, number: {}, caption: {}".format(query, number, caption))

        # Browse url
        self.browse_target_page(query)

        # Scroll down until target Number photos is reached
        self.scroll_to_num_of_posts(number)

        # Start crawling
        self.scrape_photo_links(number, is_hashtag=query.startswith("#"))

        # Save to directory
        self.download_and_save(dir_prefix,query)

        # Quit driver
        self._driver.quit()

    def browse_target_page(self, query):
        # Browse Hashtags
        if query.startswith('#'):
            relative_url = urljoin('explore/tags/',query.strip('#'))
        else: # Browse user page
            relative_url = query

        target_url = urljoin(HOST,relative_url)

        self._driver.get(target_url)

    def scroll_to_num_of_posts(self, number):
        # Get total number of posts of page
        num_info = re.search(r'\], "count": \d+', self._driver.page_source).group()
        num_of_posts = int(re.findall(r'\d+', num_info)[0])
        print("posts: {}, number: {}".format(num_of_posts,number))
        number = number if number < num_of_posts else num_of_posts

        # scroll page until reached
        loadmore = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, CSS_LOAD_MORE))
        )
        loadmore.click()

        num_to_scroll = (number - 12) / 12 + 1
        for _ in range(num_to_scroll):
            self._driver.execute_script(SCROLL_DOWN)
            time.sleep(0.1)
            self._driver.execute_script(SCROLL_UP)
            time.sleep(0.1)

    def scrape_photo_links(self, number, is_hashtag = False):

        encased_photo_links = re.finditer(r'src="([https]+:...[\/\w \.-]*..[\/\w \.-]*'
                                          r'..[\/\w \.-]*..[\/\w \.-].jpg)', self._driver.page_source)

        photo_links = [m.group(1) for m in encased_photo_links]

        print("Number of photo_links: {}".format(len(photo_links)))

        begin = 0 if is_hashtag else 1

        self.data['photo_links'] = photo_links[begin:number+begin]

    def download_and_save(self, dir_prefix, query):
        # Check if is hashtag
        dir_name = query.lstrip('#') + '.hashtag' if query.startswith('#') else query

        dir_path = os.path.join(dir_prefix,dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        for idx, photo_link in enumerate(self.data['photo_links'],0):
            sys.stdout.write("\033[F")
            print("Downloading {} image...".format(idx+1))

            # Send image request
            res = requests.get(photo_link)

            # Filename
            _, ext = os.path.splitext(photo_link)
            filename = str(idx) + ext

            with open(os.path.join(dir_path,filename),'w') as fout:
                fout.write(res.content)

def main():
    # Arguments #
    parser = argparse.ArgumentParser(description='Instagram Crawler')
    parser.add_argument('-q', '--query', type=str, default='instagram', help="target to crawl, add '#' for hashtags")
    parser.add_argument('-n', '--number', type=int, default=12, help='Number of posts to download: integer or "all"')
    parser.add_argument('-c', '--caption', action='store_true', help='Add this flag to download caption when downloading photos')
    parser.add_argument('-d', '--dir_prefix', type=str, default='./data/', help='directory to save results')
    args = parser.parse_args()

    query = args.query
    number = args.number
    dir_prefix = args.dir_prefix
    caption = args.caption

    crawler = InstagramCrawler()
    crawler.crawl(query=query, number=number, caption=caption, dir_prefix=dir_prefix)

if __name__ == "__main__":
    main()
