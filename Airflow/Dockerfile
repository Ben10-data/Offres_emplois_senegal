# image de basz
FROM apache/airflow:2.9.0


# installation des dependances java 
USER root 

RUN apt-get update && apt-get install -y openjdk-17-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir JAVA_HOME et PATH
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"


USER airflow

# ici nous allons figé nos dependances
COPY requierements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requierements.txt 
    # pip install --no-cache-dir \
    #     scrapy==2.11.1 \
    #     pymysql \
    #     python-dotenv \
    #     pyspark \
    #     pymongo==4.8.0






