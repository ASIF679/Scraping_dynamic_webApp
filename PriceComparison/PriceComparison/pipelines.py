# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from scrapy.pipelines.images import ImagesPipeline
from decimal import Decimal


class PriceComparisonPipeline:
    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.ehmpzjhaqscychsroclf",
            password="en@zPKQ2oCq4Mb",
            host="aws-0-eu-west-2.pooler.supabase.com"
        )
        self.cur = self.conn.cursor()

        # self.conn = psycopg2.connect(
        #     dbname="price_comparison_db",
        #     user="postgres",
        #     password="1049",
        #     host="localhost"
        # )
        # self.cur = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        try:
            # Check if product already exists
            product_query = """
            SELECT id FROM products WHERE title = %s;
            """
            self.cur.execute(product_query, (item['title'],))
            product_id = self.cur.fetchone()

            # If product doesn't exist, insert it
            if product_id is None:
                insert_product_query = """
                INSERT INTO products (title, image_url, category_id)
                VALUES (%s, %s, (SELECT id FROM categories WHERE name = %s))
                RETURNING id;
                """
                self.cur.execute(insert_product_query, (item['title'], item['image_url'], item['category_name']))
                product_id = self.cur.fetchone()[0]
            else:
                product_id = product_id[0]

            # Insert or update prices
            for store_price, store_url, logo_url in zip(item['store_price'], item['store_url'], item['shop_logo_url']):
                # Remove the currency symbol and convert the store price to a decimal
                if isinstance(store_price, str):
                    store_price = Decimal(store_price.replace('£', '').replace(',', ''))
                elif isinstance(store_price, int):
                    store_price = Decimal(store_price)
                else:
                    spider.logger.error(f"Invalid store price for product: {item['title']}. Store price: {store_price}")
                    continue

                shop_query = """
                INSERT INTO shops (logo_url) VALUES (%s)
                ON CONFLICT (logo_url) DO UPDATE SET logo_url = EXCLUDED.logo_url
                RETURNING id;
                """
                self.cur.execute(shop_query, (logo_url,))
                shop_id = self.cur.fetchone()[0]

                store_query = """
                INSERT INTO stores (shop_id, store_url) VALUES (%s, %s)
                ON CONFLICT (shop_id, store_url) DO UPDATE SET shop_id = EXCLUDED.shop_id, store_url = EXCLUDED.store_url
                RETURNING id;
                """
                self.cur.execute(store_query, (shop_id, store_url))
                store_id = self.cur.fetchone()[0]

                price_query = """
                INSERT INTO prices (product_id, store_id, price, currency)
                VALUES (%s, %s, %s, 'GBP')
                ON CONFLICT (product_id, store_id) DO UPDATE SET price = EXCLUDED.price;
                """
                self.cur.execute(price_query, (product_id, store_id, store_price))

            self.conn.commit()
            spider.logger.info(f"Successfully inserted or updated product: {item['title']}")
        except Exception as e:
            spider.logger.error(f"Error inserting or updating product: {item['title']}. Error: {e}")
            self.conn.rollback()

        return item


class PriceComparisonImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['image_paths'] = image_paths
        return item

    # def process_item(self, item, spider):
    #     try:
    #         # Remove the currency symbol and convert the price to a decimal
    #         try:
    #             price = Decimal(item['price'].replace('£', '').replace(',', ''))
    #         except InvalidOperation:
    #             spider.logger.error(f"Invalid price for product: {item['title']}. Price: {item['price']}")
    #             return item
    #
    #         # Insert product
    #         product_query = """
    #         INSERT INTO products (title, image_url, category_id)
    #         VALUES (%s, %s, (SELECT id FROM categories WHERE name = %s))
    #         RETURNING id;
    #         """
    #         self.cur.execute(product_query, (item['title'], item['image_url'], item['category_name']))
    #         product_id = self.cur.fetchone()[0]
    #
    #         # Insert shops and stores
    #         for store_price, store_url, logo_url in zip(item['store_price'], item['store_url'], item['shop_logo_url']):
    #             # Remove the currency symbol and convert the store price to a decimal
    #             try:
    #                 store_price = Decimal(store_price.replace('£', '').replace(',', ''))
    #             except InvalidOperation:
    #                 spider.logger.error(f"Invalid store price for product: {item['title']}. Store price: {store_price}")
    #                 continue
    #
    #             shop_query = """
    #             INSERT INTO shops (logo_url) VALUES (%s)
    #             ON CONFLICT (logo_url) DO UPDATE SET logo_url = EXCLUDED.logo_url
    #             RETURNING id;
    #             """
    #             self.cur.execute(shop_query, (logo_url,))
    #             shop_id = self.cur.fetchone()[0]
    #
    #             store_query = """
    #             INSERT INTO stores (shop_id, store_url) VALUES (%s, %s)
    #             RETURNING id;
    #             """
    #             self.cur.execute(store_query, (shop_id, store_url))
    #             store_id = self.cur.fetchone()[0]
    #
    #             price_query = """
    #             INSERT INTO prices (product_id, store_id, price, currency)
    #             VALUES (%s, %s, %s, 'GBP')
    #             ON CONFLICT (product_id, store_id) DO UPDATE SET price = EXCLUDED.price;
    #             """
    #             self.cur.execute(price_query, (product_id, store_id, store_price))
    #
    #         self.conn.commit()
    #         spider.logger.info(f"Successfully inserted product: {item['title']}")
    #     except Exception as e:
    #         spider.logger.error(f"Error inserting product: {item['title']}. Error: {e}")
    #         self.conn.rollback()
    #
    #     return item

#
# import decimal
# import psycopg2
# from scrapy.pipelines.images import ImagesPipeline
# from decimal import Decimal
#
#
# class PriceComparisonPipeline:
#     def open_spider(self, spider):
#         # self.conn = psycopg2.connect(
#         #     dbname="postgres",
#         #     user="postgres.ehmpzjhaqscychsroclf",
#         #     password="en@zPKQ2oCq4Mb",
#         #     host="aws-0-eu-west-2.pooler.supabase.com"
#         # )
#         # self.cur = self.conn.cursor()
#
#         self.conn = psycopg2.connect(
#             dbname="price_comparison_db",
#             user="postgres",
#             password="1049",
#             host="localhost"
#         )
#         self.cur = self.conn.cursor()
#
#     def close_spider(self, spider):
#         self.conn.commit()
#         self.cur.close()
#         self.conn.close()
#
#     def process_item(self, item, spider):
#         try:
#             # Remove the currency symbol and convert the price to a decimal
#             try:
#                 price = Decimal(item['price'].replace('£', '').replace(',', ''))
#             except decimal.InvalidOperation:
#                 spider.logger.error(f"Invalid price for product: {item['title']}. Price: {item['price']}")
#                 return item
#
#             # Check if product already exists
#             product_query = """
#             SELECT id FROM products WHERE title = %s;
#             """
#             self.cur.execute(product_query, (item['title'],))
#             product_id = self.cur.fetchone()
#
#             # If product doesn't exist, insert it
#             if product_id is None:
#                 insert_product_query = """
#                 INSERT INTO products (title, image_url, category_id)
#                 VALUES (%s, %s, (SELECT id FROM categories WHERE name = %s))
#                 RETURNING id;
#                 """
#                 self.cur.execute(insert_product_query, (item['title'], item['image_url'], item['category_name']))
#                 product_id = self.cur.fetchone()[0]
#             else:
#                 product_id = product_id[0]
#
#             # Insert or update prices
#             for store_price, store_url, logo_url in zip(item['store_price'], item['store_url'], item['shop_logo_url']):
#                 # Remove the currency symbol and convert the store price to a decimal
#                 try:
#                     store_price = Decimal(store_price.replace('£', '').replace(',', ''))
#                 except decimal.InvalidOperation:
#                     spider.logger.error(f"Invalid store price for product: {item['title']}. Store price: {store_price}")
#                     continue
#
#                 shop_query = """
#                 INSERT INTO shops (logo_url) VALUES (%s)
#                 ON CONFLICT (logo_url) DO UPDATE SET logo_url = EXCLUDED.logo_url
#                 RETURNING id;
#                 """
#                 self.cur.execute(shop_query, (logo_url,))
#                 shop_id = self.cur.fetchone()[0]
#
#                 price_query = """
#                 INSERT INTO prices (product_id, shop_id, price, currency)
#                 VALUES (%s, %s, %s, 'GBP')
#                 ON CONFLICT (product_id, shop_id) DO UPDATE SET price = EXCLUDED.price;
#                 """
#
#                 self.cur.execute(price_query, (product_id, shop_id, store_price))
#
#             self.conn.commit()
#             spider.logger.info(f"Successfully inserted or updated product: {item['title']}")
#         except Exception as e:
#             spider.logger.error(f"Error inserting or updating product: {item['title']}. Error: {e}")
#             self.conn.rollback()
#
#         return item
