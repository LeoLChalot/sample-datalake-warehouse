"""
Module utilitaire pour l'initialisation des sessions Spark et des connexions
dans le cadre du projet pédagogique Architecture Médaillon.
"""

import os
from pyspark.sql import SparkSession
import psycopg2
from sqlalchemy import create_engine
import boto3

def get_spark_session(app_name="MedallionPipeline"):
    """
    Crée et configure une session PySpark adaptée au stockage MinIO (S3A)
    et au connecteur PostgreSQL JDBC.
    """
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
    spark_driver_mem = os.getenv("SPARK_DRIVER_MEMORY", "2g")

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", spark_driver_mem)
        # Support du protocole S3A pour MinIO
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        # Optimisations d'écriture Parquet
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def get_boto3_s3_client():
    """Retourne un client boto3 configuré pour MinIO local."""
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password123"),
        region_name="us-east-1"
    )

def get_postgres_engine():
    """Retourne un engine SQLAlchemy connecté à la base PostgreSQL Gold."""
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "gold_db")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "postgres123")
    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")
