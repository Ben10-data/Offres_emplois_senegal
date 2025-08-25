#  Projet Offres d’Emplois – Data Engineering

## Structure du projet

```bash
offres_emplois/
│── Airflow/                  # Orchestration des workflows ETL avec Apache Airflow
│── Datalakes/                # Stockage brut des données (Hadoop / S3)
│── Dossiers_json_excel_csv/  # Export des données sous formats JSON, Excel, CSV
│── Scraping_job/             # Scripts de scraping (Scrapy)
│── basesDeDonnees/           # Scripts de configuration / initialisation des bases (MySQL, Postgres…)
│── docker-compose.yaml       # Configuration des services Docker (Airflow, DBs)
│── requirements.txt          # Dépendances Python du projet
│── src/                      # Code source Python 
```

---

## 🚀 Objectif du projet

Mettre en place une **pipeline complète de collecte et d’analyse des offres d’emplois au sengal** :

Voici une version réécrite, plus claire et professionnelle de ton texte 👇

---

1. **Scraping** des données depuis différentes plateformes, notamment **EmploiSenegal.com** et **Senjob**.

2. **Stockage des données dans différentes bases** : **MySQL, PostgreSQL et MongoDB**.

   * Après le scraping, les données sont d’abord enregistrées dans plusieurs dossiers sous différents formats (**CSV, JSON, Excel**) afin de simuler un environnement où les fichiers sont dispersés.
   * Le pipeline permet ensuite d’**ingérer automatiquement** ces fichiers dans les bases de données correspondantes.
   * Chaque fois qu’un nouveau fichier (CSV, Excel ou JSON) est généré, il est automatiquement associé et inséré dans une base de données.

3. **Stockage brut dans un Data Lake** : toutes les données présentes dans les différentes bases sont ensuite **centralisées dans un Data Lake Hadoop**, sans traitement préalable, afin de conserver une copie brute et uniforme des informations.

---
4. **Transformation et nettoyage** des données (ETL).

5. **Orchestration** et automatisation avec **Airflow**.
6. **Visualisation & analyse**.

---
## creer un espace virtuelle 


```bash
python3 -m venv .benv     # <--- 
source .benv/bin/activate 
```

## 📦 Installation des dépendances

```bash
pip install -r requirements.txt
```

---
## 🐳 Démarrage avec Docker

Lancer tous les services définis dans le projet :

```bash
docker-compose up -d
```

Arrêter les services :

```bash
docker-compose down
```

---


## 🔧 Technologies utilisées

* **Scrapy** → Collecte de données
* **PostgreSQL / MySQL /MongoDB** → Stockage bases de données 
* **Hadoop / S3** → Data Lake
* **PySpark** Ingection des bases de données vers hadoop
* **Apache Airflow** → Orchestration des workflows
* **Docker & Docker Compose** → Conteneurisation

---

## 📊 Cas d’usage

* Suivi des tendances du marché de l’emploi
* Analyse des compétences les plus demandées
* Visualisation des salaires et géolocalisation des offres

---
