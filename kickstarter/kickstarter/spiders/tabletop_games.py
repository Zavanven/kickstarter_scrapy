from time import sleep
import scrapy
from scrapy_selenium import SeleniumRequest
from random import randint


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
            category = response.selector.xpath('.//span[@id="category_filter"]/span[@class="js-title"]/text()').get()
            for project in projects:
                profile_name = project.xpath('.//div[3]/div[1]/div[2]/div/a/text()').get()
                profile_url = project.xpath('.//div[3]/div[1]/div[2]/div/a/@href').get()
                yield {
                    'project_name': project.xpath('.//h3/text()').get(),
                    'project_url': project.xpath('.//a[contains(@href, "projects")]/@href').get(),
                    'description': project.xpath('.//a[contains(@href, "projects")]/p/text()').get(),
                    'profile_name': profile_name if profile_name else project.xpath('.//div[3]/div[2]/div/div/div/div/div/span[2]/text()').get(),
                    'profile_url': profile_url if profile_url else project.xpath('.//div[3]/div[2]/div/div/div/a/@href').get(),
                    'category': category,
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


