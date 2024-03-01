from typing import Any

import scrapy
from scrapy.http import Response


class Bookspider(scrapy.Spider):
    name = 'book24_ua'
    allowed_domains = ['book24.ua']
    start_urls = ['https://book24.ua/ua/catalog/biografiya_memuary/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    def parse(self, response: Response) -> Any:
        """
        Parse the response and yield requests to follow links and next pages.

        :param response: The response to parse
        :type response: Response
        :return: Any
        """
        for link in response.xpath('//a[@class="dark_link option-font-bold font_sm"]/@href'):
            yield response.follow(link, callback=self.parse_book)

        for i in range (1):
            next_page = f'https://book24.ua/ua/catalog/biografiya_memuary/?PAGEN_1={i}/'
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """
        Parse the book information from the given response.

        Args:
            self: The object itself.
            response: The response object containing the book information.

        Yields:
            dict: A dictionary containing the parsed book information.
        """
        # Extract the book title
        title = response.css("div.topic__heading h1::text").get().strip()

        # Extract the article number
        article = response.css('span.article__value::text').get().strip()

        # Extract the category
        category = response.xpath('//span[@itemprop="name" and @class="breadcrumbs__item-name font_xs"]/text()')[
                       -2].get().strip()[2:]
        # Extract the authors
        authors = response.xpath('//div[@class="properties__value darken properties__item--inline"]/a/text()')[
            0].get().strip()

        # Extract the publisher
        publisher = response.xpath('//div[@class="properties__value darken properties__item--inline"]/a/text()')[
            1].get().strip()

        cover_elem = response.xpath('//div[contains(., "Обкладинка")]/following-sibling::div[contains(@class, "properties__value")]/text()')
        cover = cover_elem.get().strip() if cover_elem else None

        # Extract the ISBN
        isbn = response.xpath('//div[@class="properties__value darken properties__item--inline"]/text()')[
            -2].get().strip()

        # Extract the price
        price_elem = response.xpath('//span[@class="price_value"]/text()')
        price = price_elem.get().strip() if price_elem else None

        # Yield the parsed book information as a dictionary
        yield {
            'назва': title,
            'артікул': article,
            'категорія': category,
            'автори': authors,
            'видавництво': publisher,
            'обкладинка': cover,
            'isbn': isbn,
            'ціна': price,
        }

# scrapy crawl book24_ua -o data.json -s FEED_EXPORT_INDENT=4
