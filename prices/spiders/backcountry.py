import scrapy

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from prices.items import Product
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class BackcountrySpider(CrawlSpider):
  name = 'backcountry'

  def __init__(self, *args, **kwargs):
    super(BackcountrySpider, self).__init__(*args, **kwargs)
    self.allowed_domains = ['http://www.backcountry.com/', 'www.backcountry.com']
    self.base_url = 'http://www.backcountry.com'
    self.start_urls = ['http://www.backcountry.com/Store/catalog/shopAllBrands.jsp']

  def parse_start_url(self, response):
    brands = response.xpath("//a[@class='qa-brand-link']/@href").extract()

    for brand in brands:
      brand_url = str(self.base_url + brand)
      self.log("Queued up: %s" % brand_url)

      yield scrapy.Request(url = brand_url, 
                           callback = self.parse_brand_landing_pages)
  
  def parse_brand_landing_pages(self, response):
    shop_all_pattern = "//a[@class='subcategory-link brand-plp-link qa-brand-plp-link']/@href"
    shop_all_link = response.xpath(shop_all_pattern).extract()

    if shop_all_link:
      # If the link is there, click! 
      all_product_url = str(self.base_url + shop_all_link[0])  
      yield scrapy.Request(url = all_product_url,
                           callback = self.parse_product_pages)
    else: 
      # If not, start tearing into those product pages!
      yield scrapy.Request(url = response.url,
                           callback = self.parse_product_pages)

  def parse_product_pages(self, response):
    product_page_pattern = "//a[contains(@class, 'qa-product-link')]/@href"
    pagination_pattern = "//li[@class='page-link page-number']/a/@href"

    product_pages = response.xpath(product_page_pattern).extract()
    more_pages = response.xpath(pagination_pattern).extract()

    # Paginate!
    for page in more_pages:
      next_page = str(self.base_url + page)
      yield scrapy.Request(url = next_page,
                           callback = self.parse_product_pages)

    for product in product_pages:
      product_url = str(self.base_url + product)

      yield scrapy.Request(url = product_url,
                           callback = self.parse_item)

  def parse_item(self, response):

    item = Product()
    dirty_data = {}

    # Scrape the data, gotta catch 'em all!
    dirty_data['product_title'] = response.xpath("//*[@id='product-buy-box']/div/div[1]/h1/text()").extract()
    dirty_data['price'] = response.xpath("//span[@itemprop='price']/text()").extract()
    dirty_data['description'] = response.xpath("//div[@id='product-information']/div/p[2]/text()").extract()

    # Protip: Clean data early and often!
    for variable in dirty_data.keys():
      if dirty_data[variable]: 
        if variable == 'price':
          item[variable] = float(''.join(dirty_data[variable]).strip().replace('$', '').replace(',', ''))
        else: 
          item[variable] = ''.join(dirty_data[variable]).strip()

    yield item
