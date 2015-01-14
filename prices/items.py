from scrapy.item import Item, Field

class Product(Item):
  product_title = Field()
  description = Field()
  price = Field() 
