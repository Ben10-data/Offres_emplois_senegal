# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapjobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Emploi_senegal(scrapy.Item):

    poste = scrapy.Field()
    entreprise = scrapy.Field()
    niveau_etude = scrapy.Field()
    niveau_experience = scrapy.Field()
    contrat_propose = scrapy.Field()
    region = scrapy.Field()
    Competence = scrapy.Field()
    date_de_publication = scrapy.Field()
    formation = scrapy.Field()

class Dakar_Emploi(scrapy.Item):
    poste = scrapy.Field()
    entreprise = scrapy.Field()
    region = scrapy.Field()
    contract_propose = scrapy.Field()
    date_de_publication = scrapy.Field()


class SenJob(scrapy.Item):
    poste = scrapy.Field()
    region = scrapy.Field()
    date_de_publication = scrapy.Field()





    



