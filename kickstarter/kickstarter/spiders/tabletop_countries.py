from time import sleep
import scrapy
import json
import logging
import sys
import re
from random import randint
from pathlib import Path
from scrapy_selenium import SeleniumRequest



class TabletopCountriesSpider(scrapy.Spider):
    name = 'tabletop_countries'
    countries = None
    random_seed = randint(2710000, 2714299)
    index = 0

    def start_requests(self):
        try:
            with open('woeid_countries.json', 'r') as f:
                self.countries = json.load(f)
        except FileNotFoundError:
            logging.FATAL('No such file "woeid_countries.json"')
            sys.exit(1)

        yield SeleniumRequest(
            url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id=0&sort=newest&seed={self.random_seed}&page=1',
            callback=self.parse,
            wait_time=7,
            meta={
                'new_proxy': False,
            }
        )

    def parse(self, response):
        x = len(self.countries)
        if self.index < x:
            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={self.countries[self.index]["woeid"]}&sort=newest&seed={self.random_seed}&page=1',
                callback=self.parse_country,
                wait_time=7,
                meta={
                    'new_proxy': False,
                    'woeid': self.countries[self.index]["woeid"],
                }
            )
            self.index += 1
    
    def parse_country(self, response):
        if response.selector.xpath('//div[@class="page-title"]/h1[contains(text(), "bot")]'):
            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={response.meta["woeid"]}&sort=newest&seed={self.random_seed}&page=1',
                callback=self.parse_country,
                wait_time=7,
                meta={
                    'new_proxy': True,
                    'woeid': response.meta['woeid'],
                }
            )
        else:
            number_of_projects = str(response.selector.xpath('//b[@class="count ksr-green-500"]/text()').get())
            number_of_projects = self.get_number_of_projects(number_of_projects)

            yield {
                'country': response.selector.xpath('//span[@id="location_filter"]/span/text()').get(),
                'woeid': response.meta['woeid'],
                'projects': number_of_projects,
            }

            sleep(randint(5,10))

            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={response.meta["woeid"]}&sort=newest&seed={self.random_seed}&page=1',
                callback=self.parse,
                meta={
                    'new_proxy': False,
                }
            )

    def get_number_of_projects(self, text: str) -> int:
        number = re.findall(r'\d', text)
        return int("".join(number))