from time import sleep
import scrapy
from scrapy_selenium import SeleniumRequest
from random import randint


class TabletopGamesSpider(scrapy.Spider):
    name = 'tabletop_games'
    allowed_domains = ['www.kickstarter.com']
    random_seed = randint(2710000, 2714299)
    page = 1
    
    def start_requests(self):
        yield SeleniumRequest(
            url=f'https://www.kickstarter.com/discover/advanced?category_id=34&sort=newest&seed={self.random_seed}&page=1',
            callback=self.parse,
            wait_time=7,
            meta={
                'new_proxy': True,
            }
        )

    def parse(self, response):
        if not response.selector.xpath("//div[@id='global-header']"):
            yield SeleniumRequest(
                url=f'https://www.kickstarter.com/discover/advanced?category_id=34&sort=newest&seed={self.random_seed}&page={self.page}',
                callback=self.parse,
                wait_time=7,
                meta={
                    'new_proxy': True,
                }
            )
        else:
            projects = response.selector.xpath("//div[@id='projects_list']/div/div/div/div/div")
            for project in projects:
                yield {
                    'project_name': project.xpath('.//h3/text()').get(),
                    'project_url': project.xpath('.//a[contains(@href, "projects")]/@href').get(),
                    'description': project.xpath('.//a[contains(@href, "projects")]/p/text()').get(),
                    'profile_name': project.xpath('//a[contains(@href, "profile")]/text()').get(),
                    'profile_url': project.xpath('//a[contains(@href, "profile")]/@href').get(),
                    
                }

            self.page += 1
            sleep(7)

            if projects:
                yield SeleniumRequest(
                    url=f'https://www.kickstarter.com/discover/advanced?category_id=34&sort=newest&seed={self.random_seed}&page={self.page}',
                    callback=self.parse,
                    wait_time=7,
                    meta={
                        'new_proxy': False,
                    }
                )


