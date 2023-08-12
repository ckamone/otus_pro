import asyncio
import logging

from typing import Union
import requests
import aiofiles
from aiofiles import os as aioos
from bs4 import BeautifulSoup, Tag
from requests import Response
from optparse import OptionParser

import asyncio
import logging
from time import sleep
from urllib.parse import urlparse, urlunparse

# CONSTANTS
PROTO = 'https'
WEBSITE = 'news.ycombinator.com'
SUCCESS = range(200, 300)
REDIRECT = range(300, 400)
FORBIDDEN = 403
NOT_FOUND = 404


class Article:
    def __init__(self, id, link, art_type, num):
        self.id = id
        self.link = link
        self.art_type = art_type
        self.num = num


class DownloadedArticle:
    def __init__(self, id, content, encoding, art_type, num, article):
        self.id = id
        self.content = content
        self.encoding = encoding
        self.art_type = art_type
        self.num = num
        self.article = article


class Crawler:
    def __init__(self,
                 destination_dir: str,
                 resources: Union[dict, None] = None,
                 update_cycle: int = 360,
                 retry_max: int = 5):
        self.update_cycle = update_cycle
        self.destination_dir = destination_dir
        self.resources = resources
        self.retry_max = retry_max
        self.downloads = 0

    @classmethod
    def validate_link(cls, link: str) -> bool:
        if all(lambda ext: not link.endswith(ext) for ext in ['.pdf', '.txt', '.png', '.jpg']):
            return True
        return False
    
    @classmethod
    async def get_decoded_content(cls, response: requests.Response) -> (str, str):
        try:
            encoding = response.encoding.lower()
            return response.content.decode(encoding), encoding
        except Exception as e:
            raise TypeError(e)
    
    @classmethod
    def validate_response_status(cls, r):
        logging.debug(f"STATUS: {r.status_code}")
        if r.status_code in SUCCESS or r.status_code in REDIRECT:
            return True
        if r.status_code == FORBIDDEN or r.status_code == NOT_FOUND:
            raise TypeError(f'Page not found or requires authorization, {r.status_code}, {r.links}')
        return False
    
    @classmethod
    def validate_response_content_type(cls, r):
        logging.debug(f"CONTENT-TYPE: {r.headers.get('content-type', '')}")
        if 'text/html' in r.headers.get('content-type', ''):
            return True
        return False
    
    @classmethod
    def get_html(cls, uri):
        logging.debug(f"Processing URI: {uri}")
        try:
            response = requests.get(uri, timeout=3)
            if Crawler.validate_response_status(response):
                if Crawler.validate_response_content_type(response):
                    return response
                else:
                    raise TypeError(f'Page content is of other than text/html type: {uri}')
            raise ValueError(f'Page could not be processed right now: {uri}')
        except (ConnectionResetError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.RetryError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.SSLError,
                ConnectionError,
                requests.exceptions.ConnectionError) as e:
            raise ValueError(e)
        
    @classmethod
    async def get_html_async(cls, uri):
        return await asyncio.to_thread(Crawler.get_html, uri)
    
    @classmethod
    def get_correct_url(cls, url: str, scheme: str, host: str) -> str:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme or scheme
        netloc = parsed_url.netloc or host
        new_url = urlunparse((scheme, netloc, parsed_url.path,
                            parsed_url.params, parsed_url.query, ''))
        return new_url

    async def get_updates(self):
        link = Crawler.get_correct_url('', PROTO, WEBSITE)
        home = Article(id=-1, link=link, art_type='home', num=0)
        home_content = await self.get_article(home)
        content_soup = BeautifulSoup(home_content.content, 'html.parser')
        things: list[Tag,] = content_soup.find_all(attrs={'class': 'athing'})

        logging.info(f"Got {len(things)} articles in top.")
        current_top_ids = [thing.get('id') for thing in things]

        queued_resources_not_in_top = [key for key in self.resources.keys() if key not in current_top_ids]
        if queued_resources_not_in_top:
            for key in queued_resources_not_in_top:
                self.resources.pop(key)
            logging.info(f"Cleared {len(queued_resources_not_in_top)} from queue, which are not in top anymore.")

        for thing in things:
            thing_id = thing.get('id')
            if thing_id not in self.resources:
                link = thing.find('span', attrs={'class': 'titleline'}).find('a').get('href')
                link = Crawler.get_correct_url(link, PROTO, WEBSITE)
                if Crawler.validate_link(link):
                    article = Article(id=thing_id, link=link, art_type='article', num=0)
                    self.resources[thing_id] = {article: 0}
                link = Crawler.get_correct_url(f"/item?id={thing_id}", PROTO, WEBSITE)
                comment = Article(id=thing_id, link=link, art_type='comment', num=0)
                self.resources[thing_id][comment] = 0

        to_download: list = list()
        for thing_id, articles in self.resources.items():
            for article, retries in articles.items():
                if 0 <= retries <= self.retry_max:
                    to_download.append(article)

        logging.info(f"Got {len(to_download)} articles to download at current cycle.")
        await asyncio.gather(*[self.process_resource(article) for article in to_download], return_exceptions=True)

    async def process_resource(self, article: Article) -> Union[bool, BaseException]:
        da = await self.get_article(article)
        return await self.save_resource(da)

    async def get_article(self, article: Article):
        logging.info(f"Downloading {article.link}...")
        try:
            response: Response = await Crawler.get_html_async(article.link)
            content, encoding = await Crawler.get_decoded_content(response)
            d_article = DownloadedArticle(id=article.id,
                                          content=content,
                                          encoding=encoding,
                                          art_type=article.art_type,
                                          num=article.num,
                                          article=article)
            if article.art_type == 'comment':
                content_soup = BeautifulSoup(content, 'html.parser')
                span_tags: list[Tag,] = content_soup.find_all('span', attrs={'class': 'commtext'})
                link_tags: list[Tag,] = list()
                for span_tag in span_tags:
                    link_tags += span_tag.find_all('a')
                links = [link.get('href') for link in link_tags]
                links = list(set(links))
                for num, link in enumerate(links):
                    link = Crawler.get_correct_url(link, PROTO, WEBSITE)

                    resource = Article(id=article.id, link=link, art_type='resource', num=num)
                    if resource not in self.resources[article.id]:
                        self.resources[article.id][resource] = 0

        except (TypeError, ValueError) as e:
            d_article = DownloadedArticle(id=article.id,
                                          content=e,
                                          encoding='',
                                          art_type=article.art_type,
                                          num=article.num,
                                          article=article)
        return d_article

    async def save_resource(self, da: DownloadedArticle) -> Union[bool, BaseException]:
        await aioos.makedirs(f'{self.destination_dir}/{da.id}', exist_ok=True)
        if not isinstance(da.content, (ValueError, TypeError)):
            filename = f'{self.destination_dir}/{da.id}/{da.art_type}{da.num}.html'
            async with aiofiles.open(filename, 'w', encoding=da.encoding) as f:
                await f.write(da.content)
                logging.info(f'Saved news: {da.id} - {da.art_type} - {da.num}')
                self.resources[da.id][da.article] = -1
                self.downloads += 1
                return True
        elif isinstance(da.content, ValueError):
            logging.warning(da.content)
            self.resources[da.id][da.article] += 1
        else:
            if isinstance(da.content, TypeError):
                logging.warning(da.content)
                self.resources[da.id][da.article] = -2
        return False
    

def main(crawler):
    while True:
        logging.info('Checking updates...')
        try:
            asyncio.run(crawler.get_updates())

        except ValueError as e:
            logging.error(e)
        total = 0
        to_go = 0
        for resources in crawler.resources.values():
            total += sum(1 for _ in resources.values())
            to_go += sum(1 for retries in resources.values() if 0 <= retries <= crawler.retry_max)

        logging.info(f"Resources, associated with current top: {total}")
        logging.info(f"Scheduled for download: {to_go}")
        logging.info(f"Total files saved from start: {crawler.downloads}")

        sleep(crawler.update_cycle)

if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-l", "--logfile", action="store", default=None)
    op.add_option("-p", "--path", action="store", default='downloads')
    (opts, args) = op.parse_args()

    logging.basicConfig(filename=opts.logfile, level=logging.INFO)
    crawler = Crawler(destination_dir=opts.path, resources=dict())
    main(crawler)