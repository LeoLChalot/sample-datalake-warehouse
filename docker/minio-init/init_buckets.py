import os
import time
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
access_key = os.getenv("MINIO_ROOT_USER", "admin")
secret_key = os.getenv("MINIO_ROOT_PASSWORD", "password123")
buckets_to_create = ["bronze", "silver"]

print(f"🔄 Initialisation MinIO : Connexion vers {endpoint}...")

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="us-east-1"
)

# Boucle d'attente active que MinIO soit prêt
max_retries = 30
for attempt in range(1, max_retries + 1):
    try:
        s3.list_buckets()
        print("✅ MinIO est prêt et accessible !")
        break
    except (EndpointConnectionError, Exception) as e:
        print(f"⏳ Attente de MinIO... ({attempt}/{max_retries})")
        time.sleep(2)
else:
    print("❌ Impossible de joindre MinIO après plusieurs tentatives.")
    exit(1)

# Création des buckets requis
for bucket_name in buckets_to_create:
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"ℹ️ Le bucket '{bucket_name}' existe déjà.")
    except ClientError:
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' créé avec succès !")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création du bucket '{bucket_name}': {e}")

print("🎉 Initialisation des buckets MinIO terminée avec succès !")
