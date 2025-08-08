import scrapy
from scrapjob.items import Emploi_senegal
import time
import random


class EmploisenegalSpider(scrapy.Spider):
    name = "emploisenegal"
    allowed_domains = ["www.emploisenegal.com"]
    start_urls = ["https://www.emploisenegal.com/recherche-jobs-senegal"]

 
    # imitation d'un navigateur web 
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
        emplois = response.css('div.card-job-detail')
        #emploi = emplois[0]

        for emploi in emplois: 
            emploi_item = Emploi_senegal()

            emploi_item['entreprise'] = emploi.css("a.card-job-company.company-name::text").get()
            emploi_item['poste'] = emploi.css("h3 a::text").get()
            emploi_item['niveau_etude'] = emploi.css("ul li:nth-child(1) strong::text").get()
            emploi_item['niveau_experience'] = emploi.css("ul li:nth-child(2) strong::text").get()
            emploi_item['contrat_propose'] = emploi.css("ul li:nth-child(3) strong::text").get()
            emploi_item['region'] = emploi.css("ul li:nth-child(4) strong::text").get()
            emploi_item['Competence'] = emploi.css("ul li:nth-child(5) strong::text").get()
            emploi_item['date_de_publication'] = emploi.css('time::text').get()
            
            # Dans cette etape, nous allons interroger chaque bloque 
            # histoire de recuperer la formation recherché 
            mini_lien_du_formation = emploi.css("h3 a::attr(href)").get()
            lien_absolute = response.urljoin(mini_lien_du_formation)
            
            # Nous allons utiliser un boucle, au cas ou on a pas des info supplementaire
            if mini_lien_du_formation:
               yield response.follow(lien_absolute,
                              headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                },
                callback=self.parseDetail, meta = {"item":emploi_item })
            
            else: 
                yield emploi_item

        # recuperation du lien qu'on va utiliser pour faire notre scraping
        page_suivante = response.css("ul li.pager-next.active.pagination-next a::attr(href)").get()
        print(f'***************{page_suivante}***************************')
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
        else: 
            self.logger.info("Aucune page suivante trouvée - fin de la pagination")
    
    # fonction pour retrouver les informations supplementaires (la formation)
    def parseDetail(self,response):
        emploi_item = response.meta["item"] # recuperation de la classe meta 
        formation = response.css("section div.job-qualifications ul li").get()
        if formation:
            emploi_item['formation'] = formation
        else:
            emploi_item['formation'] = None 
        yield emploi_item

