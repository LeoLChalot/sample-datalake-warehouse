"""
Script de génération automatique des 5 Notebooks Jupyter pédagogiques
pour le projet Architecture Médaillon.
"""

import json
import os
import sys

# Force UTF-8 for console output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def create_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.8"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in source.strip().split("\n")]}

def code_cell(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in source.strip().split("\n")]}


# ==============================================================================
# NOTEBOOK 00 : Architecture & Connexions
# ==============================================================================
nb00_cells = [
    md_cell("""# 🏛️ Architecture Médaillon : Vue d'Ensemble & Tests d'Environnement

Bienvenue dans ce projet pédagogique complet dédié à l'**Architecture Médaillon** (Data Lakehouse).

---

## 🎯 Objectifs de ce Notebook
1. Comprendre les fondements théoriques de l'architecture Médaillon (Bronze ➔ Silver ➔ Gold).
2. Distinguer le rôle d'un **Data Lake** (MinIO) de celui d'un **Data Warehouse** (PostgreSQL).
3. Vérifier la connectivité et la santé de notre infrastructure conteneurisée avec Docker.
4. Initialiser une session **Apache Spark** configurée pour communiquer avec le stockage objet S3 local."""),

    md_cell("""---
## 1. Rappel Théorique : L'Architecture Médaillon

L'architecture Médaillon structure les données d'une entreprise en trois niveaux de raffinement successifs :

| Couche | Nom | Rôle & Caractéristiques | Format & Moteur |
| :--- | :--- | :--- | :--- |
| 🥉 **Bronze** | *Raw / Landing* | Données brutes telles quelles, immutables, avec historique complet et métadonnées d'ingestion. | Parquet / JSON / CSV sur MinIO (S3) |
| 🥈 **Silver** | *Cleaned / Conformed* | Données nettoyées, typées, dédupliquées, enrichies et filtrées des anomalies. | Parquet partitionné sur MinIO (S3) |
| 🥇 **Gold** | *Curated / Business* | Données agrégées, modélisées en étoile (faits/dimensions) et optimisées pour la BI. | Tables & Vues SQL dans PostgreSQL |

```
[ AWS S3 Open Data ]
         │
         ▼ (Ingestion brute)
  ┌──────────────┐
  │ Couche BRONZE │  MinIO S3 (Bucket 'bronze')
  └──────┬───────┘
         │
         ▼ (Nettoyage & Enrichissement PySpark)
  ┌──────────────┐
  │ Couche SILVER │  MinIO S3 (Bucket 'silver' Parquet partitionné)
  └──────┬───────┘
         │
         ▼ (Agrégations Métier & Modélisation)
  ┌──────────────┐
  │  Couche GOLD  │  PostgreSQL (Data Marts & Vues analytiques)
  └──────┬───────┘
         │
         ▼ (Visualisation décisionnelle)
  ┌──────────────┐
  │   METABASE   │  Dashboards & KPIs Business
  └──────────────┘
```"""),

    md_cell("""---
## 2. Vérification des Variables d'Environnement"""),

    code_cell("""import os
from pprint import pprint

print("=== Variables d'environnement détectées ===")
env_keys = [
    "MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY",
    "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER"
]
for k in env_keys:
    val = os.getenv(k, "NON DÉFINI (valeur par défaut)")
    if "SECRET" in k or "PASSWORD" in k:
        val = "********"
    print(f"{k:20} : {val}")"""),

    md_cell("""---
## 3. Test de Connexion au Stockage Objet (MinIO S3)

Nous utilisons la bibliothèque standard `boto3` pour vérifier que le service MinIO répond et que les buckets `bronze` et `silver` sont prêts."""),

    code_cell("""import boto3

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password123"),
    region_name="us-east-1"
)

try:
    response = s3_client.list_buckets()
    buckets = [b["Name"] for b in response.get("Buckets", [])]
    print("✅ Connexion à MinIO réussie !")
    print(f"📦 Buckets disponibles : {buckets}")
    
    for required_bucket in ["bronze", "silver"]:
        if required_bucket in buckets:
            print(f"   ✓ Bucket '{required_bucket}' est prêt.")
        else:
            print(f"   ⚠️ Bucket '{required_bucket}' manquant, création...")
            s3_client.create_bucket(Bucket=required_bucket)
            print(f"   ✓ Bucket '{required_bucket}' créé avec succès.")
except Exception as e:
    print(f"❌ Erreur de connexion à MinIO : {e}")"""),

    md_cell("""---
## 4. Test de Connexion au Data Warehouse (PostgreSQL)

Vérifions que PostgreSQL est accessible et testons une requête simple."""),

    code_cell("""from sqlalchemy import create_engine, text

pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", "gold_db")
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pwd = os.getenv("POSTGRES_PASSWORD", "postgres123")

conn_str = f"postgresql+psycopg2://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

try:
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();")).fetchone()
        print("✅ Connexion à PostgreSQL réussie !")
        print(f"🐘 Version : {result[0]}")
        
        schema_check = conn.execute(
            text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'gold';")
        ).fetchone()
        if schema_check:
            print("   ✓ Schéma 'gold' présent.")
        else:
            print("   ⚠️ Schéma 'gold' absent, création en cours...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold;"))
            conn.commit()
            print("   ✓ Schéma 'gold' créé.")
except Exception as e:
    print(f"❌ Erreur de connexion à PostgreSQL : {e}")"""),

    md_cell("""---
## 5. Démarrage et Test d'Apache Spark (PySpark avec support S3A)

Pour que Spark puisse lire et écrire dans MinIO, nous configurons le connecteur `S3A`.
Vérifions le bon fonctionnement du moteur distribué."""),

    code_cell("""from pyspark.sql import SparkSession

minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")

spark = (
    SparkSession.builder
    .appName("00_Architecture_Test")
    .master("local[*]")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
    .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
print("✅ Session PySpark initialisée avec succès !")
print(f"🔥 Version de Spark : {spark.version}")"""),

    md_cell("""### Test d'écriture et de lecture Spark vers MinIO (protocole `s3a://`)"""),

    code_cell("""# Création d'un petit DataFrame de test
test_data = [("Bronze", 1, "Raw Data"), ("Silver", 2, "Cleaned Data"), ("Gold", 3, "Business Ready")]
columns = ["Layer", "Priority", "Description"]

df_test = spark.createDataFrame(test_data, columns)
print("DataFrame de test :")
df_test.show()

# Écriture dans MinIO bucket 'bronze'
test_path = "s3a://bronze/_test_connection/medallion_layers.parquet"
df_test.write.mode("overwrite").parquet(test_path)
print(f"✓ Écrit avec succès vers {test_path}")

# Relecture depuis MinIO
df_read = spark.read.parquet(test_path)
print("Relecture depuis MinIO :")
df_read.show()
print("🎉 Test d'intégration MinIO + PySpark 100% fonctionnel !")"""),

    md_cell("""---
## 🏁 Conclusion du Notebook 00
Tous les services sont opérationnels :
- **MinIO** est accessible et prêt à recevoir les couches Bronze & Silver.
- **PostgreSQL** est prêt pour la couche Gold.
- **Apache Spark** communique sans encombre via le connecteur S3A.

👉 Passez au notebook suivant : `01_ingestion_bronze.ipynb` pour démarrer l'ingestion massive des données ouvertes d'AWS.""")
]


# ==============================================================================
# NOTEBOOK 01 : Ingestion Bronze
# ==============================================================================
nb01_cells = [
    md_cell("""# 🥉 Couche Bronze : Ingestion Massive depuis AWS S3 Open Data

---

## 🎯 Objectifs de ce Notebook
1. Comprendre la philosophie et les règles d'or de la **Couche Bronze** (Raw Landing Zone).
2. Découvrir le jeu de données public **NYC TLC Taxi Data** hébergé sur AWS Open Data.
3. Télécharger et ingérer les données brutes dans le stockage objet local **MinIO** (Bucket `bronze`).
4. Télécharger et stocker la table de référence dimensionnelle des zones géographiques (`taxi_zone_lookup.csv`).
5. Valider l'intégrité et la volumétrie sans altérer les données brutes."""),

    md_cell("""---
## 1. Les Règles d'Or de la Couche Bronze

En ingénierie des données moderne :
- **Immutabilité absolue** : On n'altère **jamais** les données brutes. Pas de filtrage, pas de déduplication, pas de renommage de colonne à ce stade.
- **Auditabilité / Rejouabilité** : Si un bug est découvert 6 mois plus tard dans un calcul métier, on doit pouvoir ré-exécuter le pipeline complet depuis les données brutes exactes.
- **Traçabilité** : On horodate et structure les fichiers bruts par date d'ingestion ou période source (`year=YYYY/month=MM/`).
- **Format natif** : On conserve le format d'origine (ici le format Parquet optimisé fourni par AWS Open Data)."""),

    md_cell("""---
## 2. Source de Données : NYC Taxi and Limousine Commission (TLC)

AWS héberge gratuitement le registre public des courses de taxis de New York :
- **Fichier des trajets (Yellow Taxi)** : ~3 millions de courses par mois contenant l'heure exacte de prise en charge/dépose, coordonnées des zones, distances, montants détaillés (pourboires, taxes, suppléments).
- **Fichier de référence (Zones)** : Table CSV associant chaque `LocationID` (1 à 265) à son `Borough` (Manhattan, Brooklyn, Queens, Bronx, Staten Island) et son quartier."""),

    code_cell("""import os
import requests
from tqdm import tqdm
import boto3

# Configuration des sources AWS Open Data
DATASET_YEAR = "2024"
DATASET_MONTH = "01"

TAXI_URL = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{DATASET_YEAR}-{DATASET_MONTH}.parquet"
ZONE_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Chemins de destination locaux temporaires
RAW_DIR = "/workspace/data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

taxi_local_path = os.path.join(RAW_DIR, f"yellow_tripdata_{DATASET_YEAR}-{DATASET_MONTH}.parquet")
zone_local_path = os.path.join(RAW_DIR, "taxi_zone_lookup.csv")

print(f"🔗 URL Taxis : {TAXI_URL}")
print(f"🔗 URL Zones : {ZONE_URL}")"""),

    md_cell("""---
## 3. Téléchargement des Données avec Barre de Progression"""),

    code_cell("""def download_file(url, target_path):
    \"\"\"Télécharge un fichier avec suivi de progression.\"\"\"
    if os.path.exists(target_path):
        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        print(f"ℹ️ Le fichier {os.path.basename(target_path)} existe déjà ({size_mb:.2f} MB). Téléchargement ignoré.")
        return
    
    print(f"⬇️ Téléchargement depuis {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    
    with open(target_path, "wb") as f, tqdm(
        desc=os.path.basename(target_path),
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    
    size_mb = os.path.getsize(target_path) / (1024 * 1024)
    print(f"✅ Téléchargé avec succès ({size_mb:.2f} MB) -> {target_path}")

# Téléchargement des deux fichiers
download_file(TAXI_URL, taxi_local_path)
download_file(ZONE_URL, zone_local_path)"""),

    md_cell("""---
## 4. Ingestion dans le Data Lake MinIO (Bucket `bronze`)

Nous stockons les fichiers dans le bucket `bronze` selon une arborescence claire et partitionnée :
- `nyc_taxi/raw_year=2024/raw_month=01/yellow_tripdata_2024-01.parquet`
- `reference/taxi_zone_lookup.csv`"""),

    code_cell("""s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password123"),
    region_name="us-east-1"
)

# Clés de stockage dans MinIO Bronze
s3_taxi_key = f"nyc_taxi/raw_year={DATASET_YEAR}/raw_month={DATASET_MONTH}/yellow_tripdata_{DATASET_YEAR}-{DATASET_MONTH}.parquet"
s3_zone_key = "reference/taxi_zone_lookup.csv"

def upload_to_bronze(local_path, s3_key):
    print(f"📤 Envoi de {os.path.basename(local_path)} vers MinIO s3://bronze/{s3_key}...")
    s3_client.upload_file(local_path, "bronze", s3_key)
    print("   ✓ Envoi terminé.")

upload_to_bronze(taxi_local_path, s3_taxi_key)
upload_to_bronze(zone_local_path, s3_zone_key)"""),

    md_cell("""---
## 5. Inspection de la Couche Bronze via PySpark

À cette étape, nous inspectons les données brutes **sans les modifier**.
Observons le schéma brut et comptons le nombre de lignes réelles enregistrées par la ville de New York."""),

    code_cell("""from pyspark.sql import SparkSession

minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")

spark = (
    SparkSession.builder
    .appName("01_Ingestion_Bronze")
    .master("local[*]")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
    .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

bronze_taxi_s3a = f"s3a://bronze/{s3_taxi_key}"
print(f"📖 Lecture directe de la couche Bronze : {bronze_taxi_s3a}")

df_bronze = spark.read.parquet(bronze_taxi_s3a)

print(f"\\n📊 Nombre de colonnes : {len(df_bronze.columns)}")
print("📋 Schéma brut :")
df_bronze.printSchema()

raw_count = df_bronze.count()
print(f"\\n🔢 Nombre total de courses brutes ingérées : {raw_count:,} lignes")"""),

    md_cell("""### Aperçu des 5 premières courses brutes"""),

    code_cell("""df_bronze.select(
    "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount"
).show(5, truncate=False)"""),

    md_cell("""### Lecture de la table de référence des Zones"""),

    code_cell("""bronze_zone_s3a = f"s3a://bronze/{s3_zone_key}"
df_zones_bronze = spark.read.option("header", "true").option("inferSchema", "true").csv(bronze_zone_s3a)

print(f"📍 Nombre total de zones géographiques : {df_zones_bronze.count()}")
df_zones_bronze.show(5)"""),

    md_cell("""---
## 🏁 Conclusion du Notebook 01
- La couche **Bronze** est alimentée avec succès dans **MinIO**.
- Nous disposons de l'intégralité du jeu de données brut (~3 millions de courses) et du référentiel des zones.
- **Rappel** : Nous n'avons effectué aucun filtre ni nettoyage. Si nous regardons de près, certaines courses comportent des montants négatifs ou des anomalies !

👉 Rendez-vous dans le notebook **`02_transformation_silver.ipynb`** pour diagnostiquer ces anomalies et concevoir notre pipeline de nettoyage et d'enrichissement !""")
]


# ==============================================================================
# NOTEBOOK 02 : Transformation Silver
# ==============================================================================
nb02_cells = [
    md_cell("""# 🥈 Couche Silver : Nettoyage, Typage & Enrichissement avec PySpark

---

## 🎯 Objectifs de ce Notebook
1. Identifier les anomalies du monde réel dans les données brutes (valeurs négatives, outliers, incohérences).
2. Appliquer les règles de nettoyage et de conformité métier.
3. Calculer des colonnes dérivées à forte valeur ajoutée (`trip_duration_minutes`, `speed_mph`, `tip_rate`).
4. Joindre les trajets avec le référentiel des zones géographiques (Boroughs de New York).
5. Sauvegarder les données nettoyées dans le bucket MinIO `silver`, optimisées en **Parquet partitionné par date**."""),

    md_cell("""---
## 1. Initialisation de la Session PySpark"""),

    code_cell("""import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")

spark = (
    SparkSession.builder
    .appName("02_Transformation_Silver")
    .master("local[*]")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
    .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.sql.parquet.compression.codec", "snappy")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
print("✅ Spark prêt pour la couche Silver !")"""),

    md_cell("""---
## 2. Chargement des Données Brutes depuis la Couche Bronze"""),

    code_cell("""# Chemins S3A vers le bucket Bronze
bronze_taxi_path = "s3a://bronze/nyc_taxi/raw_year=2024/raw_month=01/*.parquet"
bronze_zone_path = "s3a://bronze/reference/taxi_zone_lookup.csv"

df_raw = spark.read.parquet(bronze_taxi_path)
df_zones = spark.read.option("header", "true").option("inferSchema", "true").csv(bronze_zone_path)

total_raw_count = df_raw.count()
print(f"📥 Données brutes chargées : {total_raw_count:,} courses.")"""),

    md_cell("""---
## 3. Analyse Exploratoire de la Qualité des Données (Data Quality Audit)

Pourquoi la couche Silver est-elle indispensable ? Découvrons les anomalies présentes dans les données réelles de New York :"""),

    code_cell("""# 1. Montants négatifs (remboursements, contestations, erreurs de saisie)
neg_fares = df_raw.filter(F.col("fare_amount") < 0).count()
neg_total = df_raw.filter(F.col("total_amount") < 0).count()

# 2. Nombre de passagers nul ou aberrant (> 6 pour un taxi standard)
zero_passengers = df_raw.filter((F.col("passenger_count") == 0) | F.col("passenger_count").isNull()).count()

# 3. Distance nulle alors que la course est facturée
zero_dist_high_fare = df_raw.filter((F.col("trip_distance") <= 0) & (F.col("fare_amount") > 10)).count()

# 4. Dates incohérentes (en dehors de Janvier 2024)
bad_dates = df_raw.filter(
    (F.col("tpep_pickup_datetime") < "2024-01-01") | 
    (F.col("tpep_pickup_datetime") >= "2024-02-01")
).count()

print("🔍 === AUDIT DE QUALITÉ DES DONNÉES BRUTES ===")
print(f"• Courses avec montant 'fare_amount' négatif    : {neg_fares:,}")
print(f"• Courses avec montant total négatif            : {neg_total:,}")
print(f"• Courses avec 0 ou aucun passager              : {zero_passengers:,}")
print(f"• Distance nulle mais montant > $10             : {zero_dist_high_fare:,}")
print(f"• Dates aberrantes (hors janvier 2024)          : {bad_dates:,}")"""),

    md_cell("""Affichons quelques exemples de courses aberrantes pour illustrer le problème aux élèves :"""),

    code_cell("""print("Exemples de montants négatifs dans les données brutes :")
df_raw.filter(F.col("total_amount") < 0).select(
    "tpep_pickup_datetime", "trip_distance", "fare_amount", "tip_amount", "total_amount", "payment_type"
).show(5)"""),

    md_cell("""---
## 4. Pipeline de Nettoyage et de Filtrage Métier

Nous appliquons les règles de filtrage définies avec le métier :
1. **Période valide** : Prises en charge strictement comprises entre le `2024-01-01 00:00:00` et le `2024-01-31 23:59:59`.
2. **Finances saines** : `fare_amount > 0` et `total_amount > 0`.
3. **Passagers réalistes** : `passenger_count >= 1` et `passenger_count <= 8`.
4. **Distance réaliste** : `trip_distance > 0` et `trip_distance <= 100` miles.
5. **Durée de course cohérente** : Entre 1 minute et 180 minutes (3 heures)."""),

    code_cell("""# Calcul de la durée du trajet en minutes
df_with_duration = df_raw.withColumn(
    "trip_duration_minutes",
    (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60.0
)

# Application des filtres de qualité
df_cleaned = df_with_duration.filter(
    (F.col("tpep_pickup_datetime") >= "2024-01-01") &
    (F.col("tpep_pickup_datetime") < "2024-02-01") &
    (F.col("fare_amount") > 0) &
    (F.col("total_amount") > 0) &
    (F.col("passenger_count") >= 1) &
    (F.col("passenger_count") <= 8) &
    (F.col("trip_distance") > 0) &
    (F.col("trip_distance") <= 100) &
    (F.col("trip_duration_minutes") >= 1.0) &
    (F.col("trip_duration_minutes") <= 180.0)
)

cleaned_count = df_cleaned.count()
rejected_count = total_raw_count - cleaned_count
pct_retained = (cleaned_count / total_raw_count) * 100

print(f"✅ Courses conservées dans la couche Silver : {cleaned_count:,} ({pct_retained:.1f}%)")
print(f"🗑️ Anomalies filtrées                     : {rejected_count:,} ({100 - pct_retained:.1f}%)")"""),

    md_cell("""---
## 5. Enrichissement des Données (Feature Engineering)

Ajoutons des colonnes calculées indispensables pour les analystes métiers :
- `pickup_date` : Date du trajet (servira également de clé de partitionnement).
- `pickup_hour` : Heure de prise en charge (0 à 23).
- `pickup_day_of_week` : Nom du jour de la semaine (Mon, Tue, ...).
- `speed_mph` : Vitesse moyenne du véhicule en miles par heure (`distance / (durée / 60)`).
- `tip_rate` : Ratio du pourboire par rapport au tarif de base (`tip_amount / fare_amount`)."""),

    code_cell("""df_enriched = (
    df_cleaned
    .withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    .withColumn("day_of_week", F.dayofweek("tpep_pickup_datetime")) # 1=Dimanche, 2=Lundi...
    .withColumn("day_name", F.date_format("tpep_pickup_datetime", "E"))
    .withColumn("speed_mph", F.round(F.col("trip_distance") / (F.col("trip_duration_minutes") / 60.0), 2))
    .withColumn("tip_rate", F.round(F.col("tip_amount") / F.col("fare_amount"), 4))
)

# Remplacement des valeurs de vitesse aberrantes (ex: bouchon extrême ou GPS sauté)
df_enriched = df_enriched.filter(F.col("speed_mph") <= 85.0)

print("Aperçu des données enrichies :")
df_enriched.select(
    "pickup_date", "pickup_hour", "day_name", "trip_distance",
    "trip_duration_minutes", "speed_mph", "fare_amount", "tip_rate"
).show(5)"""),

    md_cell("""---
## 6. Jointure avec le Référentiel des Zones (Enrichissement Géographique)"""),

    code_cell("""# Préparation de la table des zones
zones_pu = df_zones.select(
    F.col("LocationID").alias("PULocationID"),
    F.col("Borough").alias("pickup_borough"),
    F.col("Zone").alias("pickup_zone")
)

zones_do = df_zones.select(
    F.col("LocationID").alias("DOLocationID"),
    F.col("Borough").alias("dropoff_borough"),
    F.col("Zone").alias("dropoff_zone")
)

# Jointure pour la zone de départ et la zone d'arrivée
df_silver_final = (
    df_enriched
    .join(zones_pu, on="PULocationID", how="left")
    .join(zones_do, on="DOLocationID", how="left")
    .fillna({"pickup_borough": "Unknown", "dropoff_borough": "Unknown"})
)

print("Aperçu final avec arrondissements (Boroughs) :")
df_silver_final.select(
    "pickup_date", "pickup_borough", "dropoff_borough", "trip_distance", "total_amount"
).show(5)"""),

    md_cell("""---
## 7. Sauvegarde dans MinIO Silver (Parquet Partitionné)

### 💡 Pourquoi partitionner par date ?
En partitionnant par `pickup_date`, PySpark organise le stockage physique en sous-dossiers :
`s3a://silver/nyc_taxi/pickup_date=2024-01-01/part-*.parquet`
`s3a://silver/nyc_taxi/pickup_date=2024-01-02/part-*.parquet`

Lors d'une requête analytique sur une journée spécifique, le moteur ne lira **que** le sous-dossier correspondant (**Partition Pruning**), évitant de scanner plusieurs gigaoctets inutilement !"""),

    code_cell("""silver_output_path = "s3a://silver/nyc_taxi"

print(f"💾 Écriture en cours vers {silver_output_path} (partitionné par pickup_date)...")

(
    df_silver_final
    .write
    .mode("overwrite")
    .partitionBy("pickup_date")
    .parquet(silver_output_path)
)

print("✅ Couche Silver écrite avec succès dans MinIO !")"""),

    md_cell("""Vérifions la présence des partitions écrites dans MinIO :"""),

    code_cell("""import boto3

s3_client = boto3.client(
    "s3",
    endpoint_url=minio_endpoint,
    aws_access_key_id=minio_access_key,
    aws_secret_access_key=minio_secret_key,
    region_name="us-east-1"
)

response = s3_client.list_objects_v2(Bucket="silver", Prefix="nyc_taxi/pickup_date=", MaxKeys=10)
print("Exemple de partitions créées dans le bucket Silver :")
for obj in response.get("Contents", []):
    print(f"  • {obj['Key']} ({obj['Size'] / 1024:.1f} KB)")"""),

    md_cell("""---
## 🏁 Conclusion du Notebook 02
- Nous avons transformé des données brutes bruitées en un jeu de données **Silver** propre, standardisé et enrichi.
- Les données sont stockées au format **Parquet compressé avec Snappy**, partitionné par date pour des performances optimales.

👉 Passez au notebook suivant : **`03_chargement_gold.ipynb`** pour calculer les agrégats décisionnels et alimenter notre Data Warehouse PostgreSQL !""")
]


# ==============================================================================
# NOTEBOOK 03 : Chargement Gold
# ==============================================================================
nb03_cells = [
    md_cell("""# 🥇 Couche Gold : Modélisation Décisionnelle & Chargement dans PostgreSQL

---

## 🎯 Objectifs de ce Notebook
1. Comprendre la transition du **Data Lake** (MinIO Parquet) vers le **Data Warehouse** relationnel (PostgreSQL).
2. Modéliser des **Data Marts** analytiques selon les besoins du management.
3. Calculer 3 tables de faits agrégées avec PySpark :
   - Métriques quotidiennes par arrondissement (`agg_daily_taxi_metrics`)
   - Analyse de la congestion horaire (`agg_hourly_demand`)
   - Matrice des flux entre quartiers (`agg_borough_flows`)
4. Charger la table de dimension `dim_zones` et les agrégats dans PostgreSQL.
5. Valider les performances et vérifier l'intégrité des tables Gold via SQL."""),

    md_cell("""---
## 1. Pourquoi Charger la Couche Gold dans PostgreSQL ?

| Critère | Couche Silver (Data Lake / MinIO) | Couche Gold (Data Warehouse / PostgreSQL) |
| :--- | :--- | :--- |
| **Type de données** | Trajets individuels au niveau ligne (~2.8M de lignes) | Données agrégées & tables dimensionnelles |
| **Usage type** | Data Science, Machine Learning, audits détaillés | Reporting BI, Tableaux de bord exécutifs, requêtes ad-hoc |
| **Outils consommateurs** | Apache Spark, DuckDB, Trino, scripts Python | Metabase, PowerBI, Tableau, requêtes SQL instantanées |
| **Temps de réponse** | 5 à 30 secondes (scan distribué) | Moins de 50 millisecondes (grâce aux index B-Tree) |"""),

    md_cell("""---
## 2. Initialisation de la Session PySpark et Connexion PostgreSQL"""),

    code_cell("""import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from sqlalchemy import create_engine, text
import pandas as pd

minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")

spark = (
    SparkSession.builder
    .appName("03_Chargement_Gold")
    .master("local[*]")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
    .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Connexion SQLAlchemy à PostgreSQL
pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", "gold_db")
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pwd = os.getenv("POSTGRES_PASSWORD", "postgres123")

pg_engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}")
print("✅ PySpark et PostgreSQL prêts !")"""),

    md_cell("""---
## 3. Chargement de la Couche Silver depuis MinIO"""),

    code_cell("""silver_taxi_path = "s3a://silver/nyc_taxi"
silver_zone_path = "s3a://bronze/reference/taxi_zone_lookup.csv"

df_silver = spark.read.parquet(silver_taxi_path)
df_zones_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(silver_zone_path)

print(f"📥 Couche Silver chargée : {df_silver.count():,} trajets nettoyés disponibles pour l'agrégation.")"""),

    md_cell("""---
## 4. Construction et Insertion de la Table Dimensionnelle : `dim_zones`"""),

    code_cell("""# Préparation du schéma dimensionnel pour PostgreSQL
df_dim_zones = (
    df_zones_raw
    .select(
        F.col("LocationID").alias("location_id"),
        F.col("Borough").alias("borough"),
        F.col("Zone").alias("zone_name"),
        F.col("service_zone")
    )
    .toPandas()
)

print(f"📍 Nombre de zones géographiques : {len(df_dim_zones)}")

# Insertion dans PostgreSQL
with pg_engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.dim_zones;"))
    df_dim_zones.to_sql("dim_zones", con=conn, schema="gold", if_exists="append", index=False)

print("✅ Table dimensionnelle 'gold.dim_zones' alimentée avec succès !")"""),

    md_cell("""---
## 5. Mart 1 : Métriques Quotidiennes (`agg_daily_taxi_metrics`)

Ce Data Mart répond aux questions de la direction financière et des opérations :
- Quel est le chiffre d'affaires quotidien par arrondissement ?
- Quelle est la distance moyenne et la durée moyenne d'une course chaque jour ?
- Quel est le taux de pourboire moyen ?"""),

    code_cell("""df_daily_agg = (
    df_silver
    .groupBy("pickup_date", "pickup_borough", "VendorID")
    .agg(
        F.count("*").alias("total_trips"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.sum("fare_amount"), 2).alias("total_fare"),
        F.round(F.sum("tip_amount"), 2).alias("total_tips"),
        F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
        F.round(F.avg("trip_duration_minutes"), 2).alias("avg_trip_duration_min"),
        F.round(F.avg("tip_rate"), 4).alias("avg_tip_rate")
    )
    .withColumnRenamed("pickup_borough", "borough")
    .withColumnRenamed("VendorID", "vendor_id")
    .orderBy("pickup_date", "borough")
)

print("Aperçu du Data Mart Quotidien :")
df_daily_agg.show(5)

# Conversion en Pandas pour insertion optimisée dans Postgres
pdf_daily = df_daily_agg.toPandas()
print(f"📊 Volume de lignes agrégées : {len(pdf_daily)}")

with pg_engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.agg_daily_taxi_metrics;"))
    pdf_daily.to_sql("agg_daily_taxi_metrics", con=conn, schema="gold", if_exists="append", index=False)

print("✅ Table 'gold.agg_daily_taxi_metrics' alimentée dans PostgreSQL !")"""),

    md_cell("""---
## 6. Mart 2 : Analyse de la Demande Horaire & Vitesse (`agg_hourly_demand`)

Ce Data Mart permet d'analyser les heures de pointe (rush hours), la congestion du trafic et la vitesse moyenne à New York selon le moment de la semaine."""),

    code_cell("""df_hourly_agg = (
    df_silver
    .groupBy("pickup_hour", "day_of_week", "day_name")
    .agg(
        F.count("*").alias("total_trips"),
        F.round(F.avg("trip_duration_minutes"), 2).alias("avg_duration_min"),
        F.round(F.avg("speed_mph"), 2).alias("avg_speed_mph"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue")
    )
    .orderBy("pickup_hour", "day_of_week")
)

print("Aperçu du Data Mart Horaire :")
df_hourly_agg.show(5)

pdf_hourly = df_hourly_agg.toPandas()

with pg_engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.agg_hourly_demand;"))
    pdf_hourly.to_sql("agg_hourly_demand", con=conn, schema="gold", if_exists="append", index=False)

print("✅ Table 'gold.agg_hourly_demand' alimentée dans PostgreSQL !")"""),

    md_cell("""---
## 7. Mart 3 : Matrice des Flux entre Arrondissements (`agg_borough_flows`)

Ce Data Mart met en lumière les trajets les plus fréquents et les plus lucratifs (ex: Manhattan ➔ JFK / Queens)."""),

    code_cell("""df_flows_agg = (
    df_silver
    .groupBy("pickup_borough", "dropoff_borough")
    .agg(
        F.count("*").alias("total_trips"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.avg("trip_duration_minutes"), 2).alias("avg_duration_min")
    )
    .orderBy(F.desc("total_trips"))
)

print("Top 5 des flux entre arrondissements :")
df_flows_agg.show(5)

pdf_flows = df_flows_agg.toPandas()

with pg_engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE gold.agg_borough_flows;"))
    pdf_flows.to_sql("agg_borough_flows", con=conn, schema="gold", if_exists="append", index=False)

print("✅ Table 'gold.agg_borough_flows' alimentée dans PostgreSQL !")"""),

    md_cell("""---
## 8. Validation dans PostgreSQL avec Requêtes SQL

Exécutons une requête SQL directement sur la vue métier `gold.v_top_performing_boroughs` créée dans PostgreSQL lors de l'initialisation du schéma."""),

    code_cell("""with pg_engine.connect() as conn:
    query = text(\"\"\"
        SELECT 
            borough,
            total_rides,
            gross_revenue,
            overall_avg_distance,
            avg_tip_percentage
        FROM gold.v_top_performing_boroughs;
    \"\"\")
    df_result = pd.read_sql(query, conn)

print("🏆 Résultat de la vue SQL métier dans PostgreSQL :")
print(df_result.to_string(index=False))"""),

    md_cell("""---
## 🏁 Conclusion du Notebook 03
- Les données ont franchi la dernière étape du pipeline : **la Couche Gold**.
- Les Data Marts sont structurés, indexés et stockés dans PostgreSQL.
- Les analystes métier et les décideurs peuvent désormais interroger ces tables avec des temps de réponse instantanés.

👉 Passez au notebook **`04_exploration_et_metabase.ipynb`** pour explorer les visualisations BI avec **Metabase** !""")
]


# ==============================================================================
# NOTEBOOK 04 : Exploration & Metabase
# ==============================================================================
nb04_cells = [
    md_cell("""# 📊 Couche Restitution : Analytics Avancés & Guide Metabase

---

## 🎯 Objectifs de ce Notebook
1. Valider la couche Gold à travers des requêtes SQL décisionnelles avancées (Window Functions, Pénétrations).
2. Guider pas-à-pas la connexion et la configuration de l'outil de Business Intelligence **Metabase**.
3. Réaliser des visualisations métiers clés (KPIs, Graphiques temporels, Cartes de chaleur des heures de pointe).
4. Fournir une synthèse pédagogique et des sujets d'approfondissement pour les élèves."""),

    md_cell("""---
## 1. Analyses SQL Avancées sur la Couche Gold

Interrogeons notre Data Warehouse PostgreSQL avec des fonctions de fenêtrage SQL (`WINDOW FUNCTIONS`) pour observer la part de marché relative de chaque arrondissement."""),

    code_cell("""import os
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", "gold_db")
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pwd = os.getenv("POSTGRES_PASSWORD", "postgres123")

engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}")

sql_market_share = \"\"\"
SELECT 
    borough,
    SUM(total_revenue) AS total_revenue,
    ROUND(SUM(total_revenue) * 100.0 / SUM(SUM(total_revenue)) OVER(), 2) AS revenue_pct,
    SUM(total_trips) AS total_trips,
    ROUND(SUM(total_trips) * 100.0 / SUM(SUM(total_trips)) OVER(), 2) AS trips_pct
FROM gold.agg_daily_taxi_metrics
GROUP BY borough
ORDER BY total_revenue DESC;
\"\"\"

with engine.connect() as conn:
    df_share = pd.read_sql(text(sql_market_share), conn)

print("📈 Part de marché des revenus et des volumes par arrondissement :")
print(df_share.to_string(index=False))"""),

    md_cell("""Visualisons la vitesse moyenne du trafic new-yorkais au fil de la journée :"""),

    code_cell("""sql_speed = \"\"\"
SELECT 
    pickup_hour,
    ROUND(AVG(avg_speed_mph), 2) AS avg_speed,
    SUM(total_trips) AS total_volume
FROM gold.agg_hourly_demand
GROUP BY pickup_hour
ORDER BY pickup_hour;
\"\"\"

with engine.connect() as conn:
    df_speed = pd.read_sql(text(sql_speed), conn)

plt.figure(figsize=(10, 4))
plt.plot(df_speed["pickup_hour"], df_speed["avg_speed"], marker="o", color="#2563eb", linewidth=2.5, label="Vitesse Moyenne (mph)")
plt.title("Évolution de la vitesse moyenne des taxis à New York par heure", fontsize=12, fontweight="bold")
plt.xlabel("Heure de la journée (0h - 23h)")
plt.ylabel("Vitesse (mph)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.xticks(range(0, 24))
plt.legend()
plt.tight_layout()
plt.show()"""),

    md_cell("""---
## 2. Guide Pas-à-Pas : Configuration de Metabase

**Metabase** est déjà démarré dans notre stack Docker Compose !

### Étape 1 : Accéder à l'interface Web
- Ouvrez votre navigateur sur : **[http://localhost:3000](http://localhost:3000)**
- Cliquez sur **"Let's get started"** (Créer un compte administrateur local, ex: `admin@formation.local` / `AdminPassword123!`).

### Étape 2 : Connecter la base de données PostgreSQL (Gold)
Renseignez les champs de connexion suivants :
- **Type de base de données** : `PostgreSQL`
- **Nom d'affichage** : `NYC Taxi Data Warehouse (Gold)`
- **Host** : `postgres` *(nom du service dans le réseau Docker)*
- **Port** : `5432`
- **Database name** : `gold_db`
- **Username** : `postgres`
- **Password** : `postgres123`
- Validez la connexion. Metabase va synchroniser automatiquement les tables du schéma `gold`.

```
        ┌──────────────────────────────────────────────┐
        │ Configuration de la Connexion Metabase       │
        ├──────────────────────────────────────────────┤
        │ Database Type : PostgreSQL                   │
        │ Name          : NYC Taxi Gold Warehouse      │
        │ Host          : postgres                     │
        │ Port          : 5432                         │
        │ Database Name : gold_db                      │
        │ Username      : postgres                     │
        │ Password      : postgres123                  │
        └──────────────────────────────────────────────┘
```"""),

    md_cell("""---
## 3. Idées de Visualisations Clés à Construire dans Metabase

Voici les 5 cartes à créer pour constituer le Dashboard exécutif de l'entreprise :

### 1. KPI Card : Chiffre d'Affaires Global
- **Table** : `gold.agg_daily_taxi_metrics`
- **Agrégation** : `Sum of Total Revenue`
- **Format** : Devise ($ USD).

### 2. Graphique Linéaire : Évolution Quotidienne des Revenus
- **Table** : `gold.agg_daily_taxi_metrics`
- **Axe X** : `Pickup Date`
- **Axe Y** : `Sum of Total Revenue`
- **Série groupée** : `Borough` (pour comparer Manhattan, Queens, Brooklyn).

### 3. Diagramme en Barres : Vitesse Moyenne vs Heures de Pointe
- **Table** : `gold.agg_hourly_demand`
- **Axe X** : `Pickup Hour`
- **Axe Y** : `Average of Avg Speed Mph`
- Permet de repérer instantanément le creux de vitesse entre 16h et 19h (embouteillages).

### 4. Diagramme Circulaire (Donut) : Répartition des Courses par Arrondissement
- **Table** : `gold.agg_daily_taxi_metrics`
- **Mesure** : `Sum of Total Trips`
- **Dimension** : `Borough`.

### 5. Tableau Croisé : Matrice Origine ➔ Destination
- **Table** : `gold.agg_borough_flows`
- **Lignes** : `Pickup Borough`
- **Colonnes** : `Dropoff Borough`
- **Cellules** : `Sum of Total Revenue`."""),

    md_cell("""---
## 🎓 Synthèse Pédagogique & Exercices pour les Étudiants

### Ce que les élèves ont appris :
1. **Stockage Objet vs Base Relationnelle** : Pourquoi le Data Lake (MinIO) stocke l'historique brut et les tables volumineuses, tandis que PostgreSQL sert d'accélérateur pour la BI.
2. **Le Contrat de la Couche Bronze** : Ne jamais modifier les données brutes, garantir l'auditabilité et la reproductibilité.
3. **La Valeur de la Couche Silver** : Détection des données aberrantes, normalisation des formats, enrichissement vectorisé avec PySpark.
4. **La Modélisation Gold** : Concevoir des agrégats performants pour éliminer la latence côté tableau de bord.

---

### 🚀 Défis & Projets d'Approfondissement pour les Élèves :
- **Exercice 1 (Multi-mois)** : Adapter le notebook `01_ingestion_bronze` pour ingérer plusieurs mois consécutifs (`2024-01`, `2024-02`, `2024-03`) et tester la puissance du partitionnement Spark.
- **Exercice 2 (Second Dataset)** : Télécharger le jeu de données des **Green Taxis** ou **For-Hire Vehicles (FHV)** et concevoir une couche Silver unifiée.
- **Exercice 3 (Croisement Météo)** : Télécharger un jeu de données météo public (ex: NOAA sur S3) et corréler les jours de pluie new-yorkais avec la demande de taxis et les pourboires !
- **Exercice 4 (Gestion Incrémentale)** : Implémenter une logique d'ingestion incrémentale (CDC ou `MERGE`) plutôt que de recharger l'intégralité de la base à chaque exécution.""")
]

# Write all notebooks
notebooks_to_generate = [
    ("00_architecture_et_connexions.ipynb", nb00_cells),
    ("01_ingestion_bronze.ipynb", nb01_cells),
    ("02_transformation_silver.ipynb", nb02_cells),
    ("03_chargement_gold.ipynb", nb03_cells),
    ("04_exploration_et_metabase.ipynb", nb04_cells),
]

output_dir = "c:/Users/llaro/Desktop/architecture medaillon/notebooks"
for filename, cells in notebooks_to_generate:
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(create_notebook(cells), f, indent=1, ensure_ascii=False)
    print(f"✓ Notebook généré : {filename}")

print("\\nTous les notebooks ont été générés avec succès !")
