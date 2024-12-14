# import scrapy
# from playwright.sync_api import sync_playwright
# from scrapy.crawler import CrawlerProcess
# from w3lib.html import remove_tags
#
#
# class ProductDetailsSpider(scrapy.Spider):
#     name = "product_details_spider"
#
#     def __init__(self):
#         self.playwright = None
#         self.browser = None
#         self.page = None
#
#     def start_requests(self):
#         # urls = ['https://buywisely.com.au/category/Laptops?size=n_30_n']
#         urls = ['https://buywisely.com.au/category/Laptops?current=n_2_n&size=n_150_n']
#
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def parse(self, response):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(response.url)
#         self.page.wait_for_timeout(5000)
#         self.page.wait_for_selector('div.MuiBox-root.css-agvi2e:last-child')
#         content = self.page.content()
#
#         selector = scrapy.Selector(text=content)
#         for product in selector.css('div.MuiBox-root.css-agvi2e'):
#             product_link = product.css('div.MuiBox-root.css-0 > a::attr(href)').get()
#             img_url = selector.css('div.MuiBox-root.css-t0y4rt a img::attr(src)').get()
#             yield response.follow(f"https://buywisely.com.au{product_link}", self.parse_product,
#                                   meta={'product_link': product_link, 'img_url': img_url})
#
#         # Handle pagination if present
#         current_page = int(response.url.split('=')[1].split('&')[0].split('_')[1])  # getting cur page number
#         print(current_page)
#         next_page = f"https://buywisely.com.au/category/Laptops?current=n_{current_page + 1}_n&size=n_150_n"
#         yield response.follow(next_page, self.parse)
#
#     def parse_product(self, response):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(response.url)
#         self.page.wait_for_timeout(5000)
#         self.page.wait_for_selector('div.MuiPaper-root:last-child')
#         content = self.page.content()
#         selector = scrapy.Selector(text=content)
#
#         title = selector.css('h1[class*="css-1nggc2o"]::text').extract_first()
#         price = selector.css('h2[class*="css-8t0bjo"]::text').extract_first()
#         output = selector.css('div.MuiBox-root.css-1ebprri > div > span').getall()
#         output = ' '.join(output)
#         description = remove_tags(output).strip()
#         while True:
#             for product in selector.css('div.MuiPaper-root'):
#                 # shop_link = product.css('a[href^="/shop/"]::attr(href)').get()
#                 store_name = product.css(
#                     'a[target="_blank"] > p.MuiTypography-root.MuiTypography-body1::text').get().strip()
#                 store_price = product.css('div.MuiStack-root.css-1abzdwk > div.MuiStack-root.css-b95f0i > '
#                                           'h3.MuiBox-root.css-mftzct::text').get().strip()
#
#                 # Check for low stock and go to store URLs
#                 go_to_store_button_selector = "p:has-text('Go to store')"
#                 go_to_store_urls = self.get_url(response.url, go_to_store_button_selector)
#                 low_stock_button_selector = "p:has-text('Low stock')"
#                 low_stock_urls = self.get_url(response.url, low_stock_button_selector)
#                 store = go_to_store_urls + low_stock_urls
#                 yield {
#                     'title': title,
#                     'price': price,
#                     'img_url': response.meta['img_url'],
#                     'description': description,
#                     'product_link': response.meta['product_link'],
#                     'store_name': store_name,
#                     'store_price': store_price,
#                     'store': store
#                 }
#
#             next_page = selector.css('a.MuiButtonBase-root.MuiIconButton-root::attr(href)').extract_first()
#             if next_page:
#                 yield response.follow(next_page, self.parse)
#             else:
#                 break
#
#     def get_url(self, page_url, button_selector):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(page_url)
#         new_tab_urls = self.get_urls_from_button(self.page, button_selector)
#
#         return new_tab_urls
#
#     def get_urls_from_button(self, page, button_selector):
#         try:
#             page.wait_for_selector(button_selector, timeout=5000)  # Timeout set to 5 seconds
#         except Exception as e:
#             print(f"No '{button_selector}' found on the page.")
#             return []
#
#         button_elements = page.query_selector_all(button_selector)
#
#         new_tab_urls = []
#         for button in button_elements:
#             try:
#                 with page.expect_popup() as popup_info:
#                     button.click()
#                 popup = popup_info.value
#                 new_tab_urls.append(popup.url)
#                 popup.close()
#             except Exception as e:
#                 print("Error occurred while processing button:", e)
#         return new_tab_urls
#
#
# process = CrawlerProcess(settings={
#     'FEED_FORMAT': 'json',
#     'FEED_URI': 'product_details.json'
# })
# process.crawl(ProductDetailsSpider)
# process.start()


# import scrapy
# from playwright.sync_api import sync_playwright
# from scrapy.crawler import CrawlerProcess
# from w3lib.html import remove_tags
#
# class ProductDetailsSpider(scrapy.Spider):
#     name = "product_details_spider"
#
#     custom_settings = {
#         'DOWNLOAD_DELAY': 3,  # Set a delay of 3 seconds between requests
#     }
#
#     def __init__(self):
#         self.playwright = None
#         self.browser = None
#         self.page = None
#
#     def start_requests(self):
#         urls = ['https://buywisely.com.au/category/Laptops?current=n_3_n&size=n_150_n']
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def parse(self, response):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(response.url)
#         self.page.wait_for_timeout(5000)
#         self.page.wait_for_selector('div.MuiBox-root.css-agvi2e:last-child')
#         content = self.page.content()
#
#         selector = scrapy.Selector(text=content)
#         for product in selector.css('div.MuiBox-root.css-agvi2e'):
#             product_link = product.css('div.MuiBox-root.css-0 > a::attr(href)').get()
#             img_url = selector.css('div.MuiBox-root.css-t0y4rt a img::attr(src)').get()
#             yield response.follow(f"https://buywisely.com.au{product_link}", self.parse_product,
#                                   meta={'product_link': product_link, 'img_url': img_url})
#
#         # Handle pagination if present
#         current_page = int(response.url.split('=')[1].split('&')[0].split('_')[1])  # getting cur page number
#         # Open the file in append mode ('a')
#         with open('current_page.txt', 'a') as f:
#             # Append the current page number to the file with a newline character
#             f.write(str(current_page) + '\n')
#
#         next_page = f"https://buywisely.com.au/category/Laptops?current=n_{current_page + 1}_n&size=n_150_n"
#         yield response.follow(next_page, self.parse)
#
#     def parse_product(self, response):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(response.url)
#         self.page.wait_for_timeout(5000)
#         self.page.wait_for_selector('div.MuiPaper-root:last-child')
#         content = self.page.content()
#         selector = scrapy.Selector(text=content)
#
#         title = selector.css('h1[class*="css-1nggc2o"]::text').extract_first()
#         price = selector.css('h2[class*="css-8t0bjo"]::text').extract_first()
#         output = selector.css('div.MuiBox-root.css-1ebprri > div > span').getall()
#         output = ' '.join(output)
#         description = remove_tags(output).strip()
#
#         for product in selector.css('div.MuiPaper-root'):
#             store_name = product.css(
#                 'a[target="_blank"] > p.MuiTypography-root.MuiTypography-body1::text').get().strip()
#             store_price = product.css('div.MuiStack-root.css-1abzdwk > div.MuiStack-root.css-b95f0i > '
#                                       'h3.MuiBox-root.css-mftzct::text').get().strip()
#
#             go_to_store_button_selector = "p:has-text('Go to store')"
#             go_to_store_urls = self.get_url(response.url, go_to_store_button_selector)
#             low_stock_button_selector = "p:has-text('Low stock')"
#             low_stock_urls = self.get_url(response.url, low_stock_button_selector)
#             store = go_to_store_urls + low_stock_urls
#             yield {
#                 'title': title,
#                 'price': price,
#                 'img_url': response.meta['img_url'],
#                 'description': description,
#                 'product_link': response.meta['product_link'],
#                 'store_name': store_name,
#                 'store_price': store_price,
#                 'store': store
#             }
#
#     def get_url(self, page_url, button_selector):
#         if not self.playwright:
#             self.playwright = sync_playwright().start()
#             self.browser = self.playwright.chromium.launch(headless=True)
#             self.page = self.browser.new_page()
#
#         self.page.goto(page_url)
#         new_tab_urls = self.get_urls_from_button(self.page, button_selector)
#
#         return new_tab_urls
#
#     def get_urls_from_button(self, page, button_selector):
#         try:
#             page.wait_for_selector(button_selector, timeout=5000)  # Timeout set to 5 seconds
#         except Exception as e:
#             print(f"No '{button_selector}' found on the page.")
#             return []
#
#         button_elements = page.query_selector_all(button_selector)
#
#         new_tab_urls = []
#         for button in button_elements:
#             try:
#                 with page.expect_popup() as popup_info:
#                     button.click()
#                 popup = popup_info.value
#                 new_tab_urls.append(popup.url)
#                 popup.close()
#             except Exception as e:
#                 print("Error occurred while processing button:", e)
#         return new_tab_urls
#
#
# process = CrawlerProcess(settings={
#     'FEED_FORMAT': 'json',
#     'FEED_URI': 'product_details.json'
# })
# process.crawl(ProductDetailsSpider)
# process.start()


import scrapy
from playwright.sync_api import sync_playwright
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class ProductDetailsSpider(scrapy.Spider):
    name = "products_details_spider"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Set a delay of 3 seconds between requests
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playwright = None
        self.browser = None
        self.page = None

    def start_requests(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        urls = ['https://buywisely.com.au/category/Laptops?current=n_26_n&size=n_80_n']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            self.page.goto(response.url)
            self.page.wait_for_timeout(5000)
            self.page.wait_for_selector('div.MuiBox-root.css-agvi2e:last-child')
            content = self.page.content()
        except TimeoutError as e:
            self.logger.error(f"TimeoutError occurred: {e}")
            return

        seen_products = set()
        selector = scrapy.Selector(text=content)
        for product in selector.css('div.MuiBox-root.css-agvi2e'):
            product_link = product.css('div.MuiBox-root.css-0 > a::attr(href)').get()
            img_url = selector.css('div.MuiBox-root.css-t0y4rt a img::attr(src)').get()
            if product_link not in seen_products:
                seen_products.add(product_link)
                yield response.follow(f"https://buywisely.com.au{product_link}", self.parse_product,
                                      meta={'product_link': product_link, 'img_url': img_url})

        # Handle pagination if present
        current_page = int(response.url.split('=')[1].split('&')[0].split('_')[1])  # getting cur page number
        next_page = f"https://buywisely.com.au/category/Laptops?current=n_{current_page + 1}_n&size=n_80_n"
        yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        try:
            self.page.goto(response.url)
            self.page.wait_for_timeout(5000)
            self.page.wait_for_selector('div.MuiPaper-root:last-child')
            content = self.page.content()
            selector = scrapy.Selector(text=content)
        except TimeoutError as e:
            self.logger.error(f"TimeoutError occurred: {e}")
            return

        title = selector.css('h1[class*="css-1nggc2o"]::text').extract_first()
        price = selector.css('h2[class*="css-8t0bjo"]::text').extract_first()
        output = selector.css('div.MuiBox-root.css-1ebprri > div > span').getall()
        description = remove_tags(' '.join(output)).strip()

        count = 2
        store = []
        while len(store) <= 1:
            store = self.get_stores(response)
            count -= 1
            if count == 0:
                return

        for product in selector.css('div.MuiPaper-root'):
            store_name = product.css(
                'a[target="_blank"] > p.MuiTypography-root.MuiTypography-body1::text').get().strip()
            store_price = product.css('div.MuiStack-root.css-1abzdwk > div.MuiStack-root.css-b95f0i > '
                                      'h3.MuiBox-root.css-mftzct::text').get().strip()
            yield {
                'title': title,
                'price': price,
                'img_url': response.meta['img_url'],
                'description': description,
                'product_link': response.meta['product_link'],
                'store_name': store_name,
                'store_price': store_price,
                'store': store
            }

    def get_stores(self, response):
        go_to_store_button_selector = "p:has-text('Go to store')"
        go_to_store_urls = self.get_url(response.url, go_to_store_button_selector)
        low_stock_button_selector = "p:has-text('Low stock')"
        low_stock_urls = self.get_url(response.url, low_stock_button_selector)
        store = go_to_store_urls + low_stock_urls
        return store

    def get_url(self, page_url, button_selector):
        self.page.goto(page_url)
        new_tab_urls = self.get_urls_from_button(self.page, button_selector)

        return new_tab_urls

    def get_urls_from_button(self, page, button_selector):
        try:
            page.wait_for_selector(button_selector, timeout=5000)  # Timeout set to 5 seconds
        except Exception as e:
            print(f"No '{button_selector}' found on the page.")
            return []

        button_elements = page.query_selector_all(button_selector)

        new_tab_urls = []
        for button in button_elements:
            try:
                with page.expect_popup() as popup_info:
                    button.click()
                popup = popup_info.value
                new_tab_urls.append(popup.url)
                popup.close()
            except Exception as e:
                print("Error occurred while processing button:", e)
        return new_tab_urls

    def close(self, reason):
        self.browser.close()
        self.playwright.stop()


# process = CrawlerProcess(settings={
#     'FEED_FORMAT': 'json',
#     'FEED_URI': 'product_details2.json'
# })
# process.crawl(ProductDetailsSpider)
# process.start()
