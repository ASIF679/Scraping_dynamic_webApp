import scrapy
from playwright.sync_api import sync_playwright
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class ProductDetailsSpider(scrapy.Spider):
    name = "product_details_spider"

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 3,  # Set a delay of 3 seconds between requests
    # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playwright = None
        self.browser = None
        self.page = None

    def start_requests(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        urls = ['https://buywisely.com.au/category/Laptops?current=n_18_n&size=n_80_n']
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
        # Open the file in append mode ('a')
        with open('current_page.txt', 'a') as f:
            # Append the current page number to the file with a newline character
            f.write(str(current_page) + '\n')

        next_page = f"https://buywisely.com.au/category/Laptops?current=n_{current_page + 1}_n&size=n_80_n"
        yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        self.page.goto(response.url)
        self.page.wait_for_timeout(2000)
        self.page.wait_for_selector('div.MuiPaper-root:last-child')
        content = self.page.content()
        selector = scrapy.Selector(text=content)

        title = selector.css('h1[class*="css-1nggc2o"]::text').extract_first()
        price = selector.css('h2[class*="css-8t0bjo"]::text').extract_first()
        output = selector.css('div.MuiBox-root.css-1ebprri > div > span').getall()
        output = ' '.join(output)
        description = remove_tags(output).strip()
        stores = []
        for product in selector.css('div.MuiPaper-root'):
            store_name = product.css(
                'a[target="_blank"] > p.MuiTypography-root.MuiTypography-body1::text').get().strip()
            store_price = product.css('div.MuiStack-root.css-1abzdwk > div.MuiStack-root.css-b95f0i > '
                                      'h3.MuiBox-root.css-mftzct::text').get().strip()

            go_to_store_button_selector = "p:has-text('Go to store')"
            # low_stock_button_selector = "p:has-text('Low stock')"

            new_tab_urls = []
            if go_to_store_button_selector:
                self.page.goto(response.url)
                try:
                    self.page.wait_for_selector(go_to_store_button_selector, timeout=5000)  # Timeout set to 5 seconds
                except Exception as e:
                    print(f"No '{go_to_store_button_selector}' found on the page.")
                    continue

                button_elements = self.page.query_selector(go_to_store_button_selector)

                if button_elements:
                    try:
                        with self.page.expect_popup() as popup_info:
                            button_elements.click()
                        popup = popup_info.value
                        new_tab_urls.append(popup.url)
                        popup.close()
                    except Exception as e:
                        print("Error occurred while processing button:", e)

            stores.append(new_tab_urls)
            yield {
                'title': title,
                'price': price,
                'img_url': response.meta['img_url'],
                'description': description,
                'product_link': response.meta['product_link'],
                'store_name': store_name,
                'store_price': store_price,
                'store': stores
            }

    def close(self, reason):
        self.browser.close()
        self.playwright.stop()


# process = CrawlerProcess(settings={
#     'FEED_FORMAT': 'json',
#     'FEED_URI': 'product2.json'
# })
# process.crawl(ProductDetailsSpider)
# process.start()
