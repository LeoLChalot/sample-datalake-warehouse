FROM python:3.11-slim

# Éviter les invites interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Installation de Java (requis pour Apache Spark), curl et utilitaires système
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    curl \
    procps \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configuration de JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /workspace

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Téléchargement des JARs Hadoop-AWS et PostgreSQL pour PySpark
# Cela permet à PySpark d'accéder directement à MinIO (S3A) et PostgreSQL sans dépendre d'une connexion Internet au runtime
RUN mkdir -p /opt/spark-extra-jars && \
    curl -sS -o /opt/spark-extra-jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -sS -o /opt/spark-extra-jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -sS -o /opt/spark-extra-jars/postgresql-42.7.2.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.2/postgresql-42.7.2.jar && \
    # Copier également dans le dossier jars de PySpark pour chargement automatique
    SPARK_JARS=$(python -c "import pyspark, os; print(os.path.join(os.path.dirname(pyspark.__file__), 'jars'))") && \
    cp /opt/spark-extra-jars/*.jar "$SPARK_JARS/"

# Exposition du port Jupyter
EXPOSE 8888

# Commande par défaut : lancement de JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.token=medallion", "--ServerApp.allow_origin=*"]
