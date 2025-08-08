import scrapy
from scrapjob.items import SenJob


class SenjobSpider(scrapy.Spider):
    name = "senjob"
    allowed_domains = ["senjob.com"]
    start_urls = ["https://senjob.com/sn/offres-d-emploi.php"]

    def start_requests(self):
         yield scrapy.Request(
            url=self.start_urls[0],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            callback=self.parse
        )
    

    def parse(self, response):
        emplois = response.css("table#offresenjobs tr")

        for emploi in emplois :
              if len(emploi.css("td")) < 2:
                   continue
              else:
                   senjob_items = SenJob()
                   try :
                        # on a rencontrer des problemes les classes utilisé pour le poste 
                        # on utilise try pour gerer cette exception 

                        poste = emploi.css("td div a span.offre_title span.offre_title::text")[0].get()
                        if not poste : 
                            poste = emploi.css("td div a::text")[0].get()

                        senjob_items['poste']= poste
                        senjob_items['region'] = emploi.css("td span.green_text_normal::text")[1].get()
                        senjob_items['date_de_publication'] = emploi.css("td span.green_text_normal::text")[0].get()
                        senjob_items['date_d_expiration'] = emploi.css("td span.green_text_normal span::text")[3].get()

                        if senjob_items['poste']:
                             yield senjob_items


                   except Exception as e :
                        self.logger.warning(f'l\'erreur trouvé esr {e}')
                        continue
            
           # recuperation du lien qu'on va utiliser pour faire notre scraping
        page_suivante = response.css('li.pager-next a::attr(href)').get()

        if page_suivante:
            url_suivante = response.urljoin(page_suivante) 
            yield scrapy.Request(
                url=url_suivante,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                },
                callback=self.parse
            )

            self.logger.info(f"Page suivante : {url_suivante}")

                        
                       




                   

                   