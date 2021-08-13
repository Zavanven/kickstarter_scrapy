import scrapy
import json
from scrapy_selenium import SeleniumRequest



class TabletopCountriesSpider(scrapy.Spider):
    name = 'tabletop_countries'
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'kickstarter.pipelines.KickstarterPipeline': 810,
    #     }
    # }

    def __init__(self):
        pass

    def start_requests(self):
        yield SeleniumRequest(
            url=f'www.kickstarter.com/discover/advanced?category_id=34&woe_id=23424804&sort=newest&page=1',
            callback=self.parse,
            wait_time=7,
            meta={
                'new_proxy': True,
            }
        )
