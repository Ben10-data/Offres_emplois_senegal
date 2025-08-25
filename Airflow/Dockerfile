FROM apache/airflow:2.9.0

USER airflow

RUN pip install --no-cache-dir \
    scrapy==2.11.1 \
    pymysql \
    dotenv \
    pyspark \
    pymongo==4.8.0 



USER root 

RUN apt-get update && apt-get install -y openjdk-17-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir JAVA_HOME et PATH
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"




