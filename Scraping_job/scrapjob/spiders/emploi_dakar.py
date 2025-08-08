import scrapy
import json
from scrapy import Selector
from scrapjob.items import Dakar_Emploi


class EmploiDakarSpider(scrapy.Spider):
    name = "emploi_dakar"
    allowed_domains = ["www.emploidakar.com"]
    start_urls = ["https://www.emploidakar.com/jm-ajax/get_listings/"]

    def __init__(self):
        self.page_suivante = 0

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            callback=self.parse
        )
    
    #Ici, nous allons utiliser l' API de Emploi_Dakar 
    def parse(self, response):
        # On recupere le recupere en fichier json 
        data = response.json()
        # Mais comme c'est complique a manipuler, nous allons les transformer 
        # en lecture html/css 
        selector = Selector(text = data["html"])
        liste_des_li = selector.css('li')

        for element in liste_des_li:
            dakar_item = Dakar_Emploi()
            
            # Condition de la recuperation des données 
            lien_a = element.css('a')
            if lien_a:
                dakar_item['poste'] = element.css("a h3::text").get()
                dakar_item['entreprise'] = element.css("a div.company strong::text").get()
                dakar_item['region'] = element.css("a div.location::text").get()
                dakar_item['contract_propose'] = element.css("a ul.meta li:nth-child(1)::text").get()
                dakar_item['date_de_publication'] = element.css("a ul.meta li:nth-child(2) time::text").get()



            yield dakar_item
        
        # Pour la pagination 
        if self.page_suivante < 18:

            self.page_suivante += 1 # nous allons innitier un conteur 
            
            # cette API utilise le meme lien, mais il change juste la page au formatdata
            yield scrapy.FormRequest(
                url = self.start_urls[0], 
                formdata={"page":str(self.page_suivante)},
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                },
            callback=self.parse
        )
       