# Scrapy settings for prices project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'prices'

SPIDER_MODULES = ['prices.spiders']
NEWSPIDER_MODULE = 'prices.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'prices (+http://www.yourdomain.com)'
