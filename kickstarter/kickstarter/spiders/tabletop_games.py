from time import sleep
import scrapy
from scrapy_selenium import SeleniumRequest
from random import randint
import json
import logging
import sys


class TabletopGamesSpider(scrapy.Spider):
    name = 'tabletop_games'
    allowed_domains = ['www.kickstarter.com']
    random_seed = randint(2710000, 2714299)
    page = 1

    custom_settings = {
        'ITEM_PIPELINES': {
            'kickstarter.pipelines.KickstarterPipeline': 810,
        }
    }
    
    def start_requests(self):
        try:
            with open('woeid_countries.json', 'r') as f:
                self.countries = json.load(f)
                self.countries_size = len(self.countries)
                self.countries_index = 0
        except FileNotFoundError:
            logging.FATAL('No such file "woeid_countries.json"')
            sys.exit(1)

        yield SeleniumRequest(
            url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={self.countries[self.countries_index]["woeid"]}&sort=newest&seed={self.random_seed}&page=1',
            callback=self.parse,
            wait_time=7,
            meta={
                'new_proxy': True,
            }
        )

    def parse(self, response):
        if response.selector.xpath("//h1[contains(text(), 'Backer or bot?')]"):
            # Run this if bot is blocked. Change to new proxy and try again.
            logging.warning('Bot has been blocked. Trying again with new proxy.')
            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={self.countries[self.countries_index]["woeid"]}&sort=newest&seed={self.random_seed}&page={self.page}',
                callback=self.parse,
                wait_time=7,
                meta={
                    'new_proxy': True,
                }
            )
        elif response.selector.xpath('//section[@id="advanced_container" and contains(@class, "no_results")]') or\
        response.selector.xpath("//h1[contains(text(), 'Back it up!')]"):
            # When there are no results on page or bot hit 201 page change to next country.
            logging.warning('No more results. Changing country.')
            self.page = 1
            self.countries_index += 1
            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={self.countries[self.countries_index]["woeid"]}&sort=newest&seed={self.random_seed}&page={self.page}',
                callback=self.parse,
                wait_time=7,
                meta={
                    'new_proxy': False,
                }
            )
        else:
            projects = response.selector.xpath("//div[@id='projects_list']/div/div/div")
            category = response.selector.xpath('.//span[@id="category_filter"]/span[@class="js-title"]/text()').get()
            for project in projects:
                project_url = project.xpath('.//a[contains(@href, "projects")]/@href').get()
                project_url = str(project_url).replace('?ref=discovery_category_newest', '')
                profile_name = project.xpath('.//div[3]/div[1]/div[2]/div/a/text()').get()
                profile_url = str(project.xpath('.//div[3]/div[1]/div[2]/div/a/@href').get()).replace('?ref=discovery_category_newest', '')
                yield {
                    'project_name': project.xpath('.//h3/text()').get(),
                    'project_state': project.xpath('.//@data-project_state').get(),
                    'backers_count': project.xpath('.//@data-project_backers_count').get(),
                    'project_pledged': project.xpath('.//@data-project_pledged').get(),
                    'percent_raised': project.xpath('.//@data-project_percent_raised').get(),                   
                    'project_url': project_url,
                    'description': project.xpath('.//@data-project_description').get(),
                    'profile_name': profile_name if profile_name else project.xpath('.//div[3]/div[2]/div/div/div/div/div/span[2]/text()').get(),
                    'profile_url': profile_url if profile_url else str(project.xpath('.//div[3]/div[2]/div/div/div/a/@href').get()).replace('?ref=discovery_category_newest', ''),
                    'category': category,
                    'country': self.countries[self.countries_index]['country']
                }

            self.page += 1
            sleep(7)

            if projects:
                # Change to next page
                yield SeleniumRequest(
                    url=f'https://www.kickstarter.com/discover/advanced?category_id=34&woe_id={self.countries[self.countries_index]["woeid"]}&sort=newest&seed={self.random_seed}&page={self.page}',
                    callback=self.parse,
                    wait_time=7,
                    meta={
                        'new_proxy': False,
                    }
                )


