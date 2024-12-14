import scrapy


class IdealoProductsSpider(scrapy.Spider):
    name = "category_spider"

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 2,
    #     'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    # }

    def start_requests(self):
        urls = ['https://www.idealo.co.uk/cat/3751/laptops.html']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        seen_products = set()
        category_name = "Laptops"
        # Extract product information from the current page
        products = response.css('div.sr-resultList__item')
        for product in products:
            title = product.css('div.sr-productSummary__title::text').get()
            # price = product.css('div.sr-detailedPriceInfo__price::text').get()
            url = product.css('div.sr-resultItemLink.sr-resultItemTile__link > a::attr(href)').get()
            image_url = product.css('div.sr-resultItemTile__imageSection img::attr(src)').get()

            if url is not None and url not in seen_products:
                seen_products.add(url)
                yield response.follow(url, self.parse_product,
                                      meta={'title': title, 'image_url': image_url,
                                            'category_name': category_name})

        # Extract the URL of the next page and send request if available
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        store_price = []
        store_url = []
        shop_logo_url = []
        products = response.css('div.column.small-24.large-12.larger-12.xlarge-12.price-column')
        for a, product in enumerate(products, start=1):
            store_url.append("https://www.idealo.co.uk" + product.xpath(
                './/a[@class="productOffers-listItemOfferPrice"]/@href').get())
            store_price.append(product.css('a.productOffers-listItemOfferPrice::text').get().strip())
            count = a * 2
            shop_logo_url.append(product.xpath(
                f'(//div[@class="productOffers-listItemOfferShopV2Logo"]//img[contains(@class, '
                f'"productOffers-listItemOfferShopV2LogoImage")])[{count}]/@src').get())

        yield {
            'title': response.meta['title'],
            'category_name': response.meta['category_name'],
            'image_url': response.meta['image_url'],
            'store_price': store_price,
            'store_url': store_url,
            'shop_logo_url': shop_logo_url,
        }
