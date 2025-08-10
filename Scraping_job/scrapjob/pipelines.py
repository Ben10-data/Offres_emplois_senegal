# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json 
import os 

class ScrapjobPipeline:
    def process_item(self, item, spider):
        return item


class Indentation_Donnee:
    def __init__(self):
        # On initialiser ou nos données seront stockés 
        self.items ={}
    
    def open_spider(self, spider):
        # iinitialise une liste pour stocker nos items 
        self.items[spider.name] = []
    
    # Ajoutons nos items dans notre self.items 
    def process_item(self,item, spider):
        if item :
            self.items[spider.name].append(dict(item))
        return item 
 
    def close_spider(self, spider):

        # creation du dossier de sortie ou pour stocker nos fichier json 
        dossier_sortie = "/opt/airflow/donnes_des_json"
        os.makedirs(dossier_sortie, exist_ok=True)

        # creation des fichiers 
        file_sortie = os.path.join(dossier_sortie, f"{spider.name}.json")

        # Stockage 
        with open(file_sortie, "w", encoding="utf-8") as f:
            json.dump(self.items[spider.name],f, indent=4, ensure_ascii=False)





    

        
