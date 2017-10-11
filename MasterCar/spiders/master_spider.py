#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import requests
import json
import re
from lxml import html, etree
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from scrapy.http.request import Request

from ..items import MastercarProductItem,MastercarPriceItem
class MasterSpider(scrapy.Spider):
    name = "master"

    def __init__(self):
        ua = UserAgent()

        self.header = {
    'Host': 'www.mcmaster.com',
    'User-Agent': ua.chrome,
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.mcmaster.com/',
    'Cookie': 'bid=178065732494; volver=mv1507668475; stbver=mvB; trkrvisit=ead9d71744d248f0874098d2b138d710; clntextrep=3467192801654961; vstrextrep=8359739499773926; sesnextrep=48474854804957; settings=SU1; MAT=U3hTSlUrOVhoVTEzZFdoYXhwUGphak52ZjlrR1NRPT0=; contentver=1506673296; rs=10',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
    }

        self.valid_data = lambda x: x[0] if len(x) > 0 else None

    def start_requests(self):
        url = 'https://www.mcmaster.com/mv1507668475/WebParts/Content/ContentWebPart/ContentWebPart.aspx?cntnrIDtxt=ProdPageContent&srchidtxt=9983803245416&cntnrwdth=1046&srchrslttxt=Standard%20Socket%20Head%20Screws&PrsnttnUsrInps=[{%22PrsnttnId%22:%221957910639475%22}]&GrpUsrInps=[{%22AnchorProdSetId%22:-1,%22AnchorStateIsSet%22:true,%22GrpEID%22:%22%22,%22ProdSetId%22:%22-1%22}]&viewporthgt=341&envrmgrcharsetind=5'
        yield Request(url=url,headers=self.header,callback= self.parse)

    def parse(self, response):
        if response.status == 200:
            doc = html.fromstring(response.body)
            all_product_id = doc.xpath("//td[contains(@class,'ItmTblCellPartNbr')]/a[@class='PartNbrLnk']/text()")
            all_product_id = list(set(all_product_id))
            for prduct_id in all_product_id[0:200]:
                print "<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>"
                print "Getting info of ID:", prduct_id
                link = "https://www.mcmaster.com/mv1507668475/WebParts/Content/ItmPrsnttnWebPart.aspx?partnbrtxt=" + str(
                    prduct_id) + "&attrcompitmids=&attrnm=&attrval=&cntnridtxt=MainContent&proddtllnkclickedInd=true&cntnrWdth=1266&cntnrHght=299&printprsnttnInd=false&screenDensity=1&envrmgrcharsetind=5"
                yield Request(url=link,callback=self.product,meta={"id":prduct_id})

    def product(self,response):
        items = MastercarProductItem()
        price_items = MastercarPriceItem()
        if response.status == 200:
            # with open("out.html", "w") as f:
            #     f.write(r.text.encode('utf-8'))
            doc = html.fromstring(response.body)
            print "processing product..."
            items["image"] = "https://www.mcmaster.com" + self.valid_data(
                doc.xpath("//div[@class='ImgCaptionCntnr ImgCaptionCntnrHover']/img/@src"))
            items["image2"] = "https://www.mcmaster.com" + self.valid_data(
                doc.xpath("//div[contains(@class,'CADImgCaptionCntnr')]/img/@src"))
            items["MFG_PART_ID"] = self.valid_data(doc.xpath("//div[contains(@class,'PartNbr')]/text()"))
            price_items["MFG_PART_ID"] = self.valid_data(doc.xpath("//div[contains(@class,'PartNbr')]/text()"))
            price_details = self.get_price(items["MFG_PART_ID"])
            price_items["price1"] = price_details[0]
            price_items["packageQty1"] = price_details[1]
            items["description2"] = self.get_all_text(
                etree.tostring(self.valid_data(doc.xpath("//h3[@class='header-primary--pd']")), method='html',
                               with_tail=False))
            items["description"] = self.get_all_text(
                etree.tostring(self.valid_data(doc.xpath("//h3[@class='header-secondary--pd']")), method='html',
                               with_tail=False))
            items["extra"] = self.get_all_text(
                etree.tostring(self.valid_data(doc.xpath("//div[@class='CpyCntnr']")), method='html', with_tail=False))

            detail_row = doc.xpath("//table[contains(@class,'spec-table')]/tr")
            items["spec"] = {}
            for row in detail_row:
                key = self.valid_data(row.xpath(".//td[1]/text()"))
                value = self.valid_data(row.xpath(".//td[2]/text()"))
                try:
                    extra_value = self.valid_data(row.xpath(".//td[2]/span/text()"))
                    if extra_value:
                        value = extra_value
                except:
                    pass

                items["spec"][self.format_key(key)] = value.replace("\"", "")
            if items:
                yield items

    def get_all_text(self,html):
        soup = BeautifulSoup(html)
        return soup.text.replace("\"", "")

    def format_key(self,key):
        if key:
            key = key.lower().replace(" ", "")
            return key

    def get_price(self,part_id):
        url = 'https://www.mcmaster.com/mv1507668475/WebParts/Content/ItmPrsnttnDynamicDat.aspx?acttxt=dynamicdat&partnbrtxt=' + str(
            part_id) + '&isinlnspec=false&attrCompIds=&attrnm=&attrval='
        r = requests.get(url=url, headers=self.header)
        if r.status_code == 200:
            price = json.loads(r.text).get("PrceTxt")
            detail_price = re.findall(r'\$?[0-9]+\.?[0-9]*', price, re.I | re.M)
            if detail_price:
                return detail_price
            else:
                return [None, None]
        else:
            return [None, None]




