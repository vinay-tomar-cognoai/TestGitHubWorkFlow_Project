import sys
import logging
import operator

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from EasySearchApp.models import *

logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(index_website_scheduler, 'interval', seconds=10)
    scheduler.add_job(crawl_website_scheduler, 'interval', seconds=5)
    scheduler.start()


def index_website_scheduler():
    from EasySearchApp.utils import index_website
    try:
        website_link_obj = WebsiteLink.objects.filter(is_indexed=False)
        if website_link_obj:
            logger.info(website_link_obj[0].link, extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            index_website(website_link_obj[0])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error index_website_scheduler %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def crawl_website_scheduler():
    from EasySearchApp.utils import crawl_weblink
    try:
        website_link_obj = WebsiteLink.objects.filter(
            is_crawl=True).exclude(index_level=None)
        if website_link_obj:
            website_link_obj[0].is_crawl = False
            website_link_obj[0].save()
            crawl_weblink(website_link_obj[0], WebsiteLink, SearchUser)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error crawl_website_scheduler %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
