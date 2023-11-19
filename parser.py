import json
import math
import time
from typing import Dict, List

import requests
from loguru import logger as log
from nested_lookup import nested_lookup
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
import re

from decouple import config
from tools import get_unique_pairs


#base_url="https://shop.nhl.com/"
company_selector = 'li.entity-item>a'
filter_selector= 'a.side-nav-facet-item.hide-radio-button'
amount_selector='[data-talos="itemCount"]'
#filter_text_selector='ul.filter-selector>li>a'


def parse_companies(base_url,scrapfly: ScrapflyClient):
    result = scrapfly.scrape(ScrapeConfig(url=base_url))
    companies = [result.soup.select(company_selector)[i].attrs['href'] for i in
             range(0, len(result.soup.select(company_selector)))]
    log.info(f"scraping commands {len(companies)}", base_url)
    return companies


def get_filters(base_url,company_link, scrapfly: ScrapflyClient):
    log.info("scraping company filters {}", company_link)
    company_page=scrapfly.scrape(ScrapeConfig(url=base_url + company_link))

    filters = get_unique_pairs([[company_page.soup.select(filter_selector)[j].attrs['href'],company_page.soup.select(filter_selector)[j].text ] for j
               in range(len(company_page.soup.select(filter_selector)))])



    return filters

def get_pages(base_url,filter,scrapfly: ScrapflyClient):
    try:
        pattern = r'\d+'
        page_content = scrapfly.scrape(ScrapeConfig(url=base_url + filter))
        amount = page_content.soup.select(amount_selector)[0].text,
        amount = int(re.findall(pattern, amount[0])[-1])
        page = math.ceil(amount / 72)
        return page
    except Exception as e:
        log.info(e)
        return 1

def parse_items(base_url,filter,page,scrapfly: ScrapflyClient) -> List:
    items = []
    try:
        for i in range(0,page):
            items.append(scrapfly.scrape(ScrapeConfig(url=base_url+filter +"?pageSize=72&pageNumber={}&sortOption=TopSellers".format(page))))
    except Exception as e:
        log.info(e)
    return items


async def scrape_items(url,scrapfly: ScrapflyClient):
    parse_url=url[0:url.index('@#$')] ### '@#$' - колхозное решение с разделителем передаваемым в урл
    log.info("scraping item {}", url)
    result = await scrapfly.async_scrape(ScrapeConfig(str(parse_url)))
    url_part=url.split('/')[4].replace('-',' ')
    if url_part.upper()==[result.soup.select('''a.breadcrumb-link''')[i].text for i in range(len(result.soup.select('''a.breadcrumb-link''')))][0].upper():
        log.info("Requesting {} by filter {} Status {}".format(url[0:url.index('@#$')],url[url.index('@#$')+3:], result.status_code))
        product = {"urs":parse_url,
                    "name":result.soup.select('''h1[data-talos="labelPdpProductTitle"]''')[0].text,
                    "slug": result.soup.select("span.breadcrumb-text")[0].text,
                    "price": result.soup.select('''div[class="layout-row pdp-price"]>div.price-card>div>div>span>span>span.money-value>span.sr-only''')[0].text,
                    "last_sale":"",
                    "filter": url[url.index('@#$')+3:], ### '@#$' - колхозное решение с разделителем передаваемым в урл
                   }

        product["gender"]=  "women" if "women" in product["urs"] else "men" if "men" in product["urs"] else "kids" if "youth" in product["urs"] else ""
        try:
            product["brand"]=result.soup.select('''body > div.layout-row > div > div:nth-child(6) > div.layout-column.large-4.medium-6.small-12 > div.layout-row.product-details > div > div.description-box-content > ul > li:nth-child(2)''')[0].text
        except:
            product["brand"] = ""
        try:
            product["description"] =result.soup.select('''div.description-box.product-description-container.collapsible''')[0].text
        except:
            product["description"] = ""
        try:
            category_list=[result.soup.select('''a.breadcrumb-link''')[i].text for i in range(len(result.soup.select('''a.breadcrumb-link''')))]
            product["category"] = category_list
        except:
            product["category"] = ""
        try:
            product["characteristics"] = {i:result.soup.select('''div.description-box-content>ul>li''')[i].text for i in range(len(result.soup.select('''div.description-box-content>ul>li''')))}
        except:
            product["characteristics"] = ""
        try:
            product["images"] = result.soup.select('''div[class="carousel-container large-pdp-image"]>div>img''')[0].attrs['src']
        except:
            product["images"] = ""
        try:
            product['variants'] = [j.text for j in result.soup.select('''a.size-selector-button.available''')]
        except:
            product['variants'] = ""
    else:
        pass

    return product

