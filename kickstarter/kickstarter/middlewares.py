from scrapy_selenium.middlewares import SeleniumMiddleware
import logging
import sys
import os
from random import choice
from selenium import webdriver
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from scrapy_selenium.http import SeleniumRequest as HttpSeleniumRequest
from selenium.webdriver.firefox.options import Options
import urllib3
import urllib
from itemadapter import is_item, ItemAdapter

class CustomSeleniumMiddleware(SeleniumMiddleware):
    def __init__(self, driver_name, driver_executable_path, driver_arguments, browser_executable_path):
        self.superagents = self.populate_useragents_list()
        self.proxies = self.get_http_proxies()
        SeleniumMiddleware.__init__(self, driver_name, driver_executable_path, driver_arguments, browser_executable_path)
    
    def get_http_proxies(self) -> list:
        '''Get list of http proxies from proxyscrape.com'''
        link = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=4000&country=all&ssl=all&anonymity=all'
        with urllib.request.urlopen(link) as f:
            text = f.read().decode('utf-8')
            return str(text).strip().replace('\r', '').split('\n')
            
    def populate_useragents_list(self):
        '''Return list of user agents for selenium'''
        try:
            superagents = list()
            script_dir = os.path.dirname(__file__)
            with open(f'{script_dir}/useragents.txt', 'r') as f:
                for line in f:
                    superagents.append(line.strip())
            return superagents
        except FileNotFoundError:
            logging.warning('Could not open/find useragents.txt')
            sys.exit(1)
    
    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, HttpSeleniumRequest):
            return None

        if request.meta['new_proxy']:
            self.change_profile()

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(
                request.wait_until
            )

        if request.screenshot:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )
    
    def change_profile(self):
        '''Changes user agent and proxy for new driver'''
        self.driver.quit()
        ip, port = self.is_good_proxy(choice(self.proxies), self.proxies)
        options = Options()
        options.headless = True
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', choice(self.superagents))
        profile.set_preference('network.proxy.http', ip)
        profile.set_preference('network.proxy.http_port', port)
        profile.set_preference('intl.accept_languages', 'en-US, en')
        self.driver = webdriver.Firefox(firefox_profile=profile, options=options)
    
    def is_good_proxy(self, string: str, proxy_list: list):
        '''Return working proxy'''
        try:
            logging.warning(f'Checking PROXY: {string}')
            address = string.split(':')
            ip = address[0]
            port = address[1]
            proxy = urllib3.ProxyManager(f'http://{ip}:{port}/')
            req = proxy.request('GET', 'https://google.com/', timeout=3.0)
            logging.warning(f'Request status: {req.status}')
            return address
        except urllib3.exceptions.MaxRetryError:
            logging.warning(f'Max retry error!')
            self.proxies.remove(string)
            logging.warning(f'Proxies left: {len(self.proxies)}')
            return self.is_good_proxy(choice(proxy_list), proxy_list)