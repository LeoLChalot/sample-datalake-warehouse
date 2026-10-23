# 🏅 Projet Pédagogique : Architecture Médaillon (Data Lakehouse)

Ce projet est un environnement d'apprentissage prêt à l'emploi conçu pour illustrer de manière concrète et reproductible les concepts fondamentaux du **Data Lake**, du **Data Warehouse** et du paradigme **Médaillon (Bronze ➔ Silver ➔ Gold)**.

L'ensemble de la pile technologique est conteneurisée via **Docker Compose**, permettant aux étudiants de démarrer l'infrastructure complète en une seule commande, sans conflit de dépendances locales.

---

## 📐 Architecture Technique Globale

```
                       [ Sources Libres ]
                  AWS S3 Public Open Datasets
                     (NYC TLC Taxi Records)
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 🥉 COUCHE BRONZE (Data Lake Raw Landing)    │
         │ MinIO S3 (Bucket: 'bronze')                  │
         │ • Données brutes immutables (Parquet & CSV)  │
         │ • Auditabilité & conservation du format brut │
         └──────────────────────┬───────────────────────┘
                                │
               PySpark / Pandas │ Nettoyage, typage,
                                │ déduplication, enrichissement
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 🥈 COUCHE SILVER (Cleaned & Conformed)       │
         │ MinIO S3 (Bucket: 'silver')                  │
         │ • Format Parquet compressé (Snappy)          │
         │ • Partitionné par date (pickup_date)         │
         │ • Enrichi (durées, vitesses, taux pourboire) │
         └──────────────────────┬───────────────────────┘
                                │
               PySpark / SQL    │ Modélisation décisionnelle
                                │ Agrégats & Data Marts
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 🥇 COUCHE GOLD (Data Warehouse / Curated)    │
         │ PostgreSQL (gold_db.gold)                    │
         │ • Table dimensionnelle : dim_zones           │
         │ • Faits agrégés : agg_daily_taxi_metrics     │
         │ • Faits horaires : agg_hourly_demand         │
         │ • Matrice de flux : agg_borough_flows        │
         └──────────────────────┬───────────────────────┘
                                │
                                │ Requêtes SQL indexées
                                ▼
         ┌──────────────────────────────────────────────┐
         │ 📊 RESTITUTION & BUSINESS INTELLIGENCE       │
         │ Metabase (Port 3000)                         │
         │ • Tableaux de bord décisionnels              │
         │ • Indicateurs financiers & de trafic         │
         └──────────────────────────────────────────────┘
```

---

## 🧰 Stack Technologique

| Composant | Rôle dans l'Architecture | Accès / Interface |
| :--- | :--- | :--- |
| **AWS S3 Open Data** | Fournisseur de données massives ouvertes (courses de taxis de New York) | Endpoint public HTTPS / S3 |
| **MinIO** | Object Storage S3 local simulant un Data Lake d'entreprise | Console Web : `http://localhost:9001`<br>API S3 : `http://localhost:9000` |
| **Apache Spark (PySpark)** | Moteur de calcul distribué pour le nettoyage et l'agrégation | Exécuté dans le conteneur Jupyter |
| **PostgreSQL 16** | Data Warehouse relationnel hébergeant la couche Gold | Port `5432` (Base : `gold_db`) |
| **Metabase** | Outil de BI libre-service pour la visualisation des Data Marts | Interface Web : `http://localhost:3000` |
| **JupyterLab** | Environnement d'orchestration pédagogique guidée pas-à-pas | Interface Web : `http://localhost:8888` |

---

## 🚀 Démarrage Rapide (Pour l'Enseignant et les Élèves)

### 1. Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS / Linux) avec au moins 4 Go de mémoire allouée.

### 2. Démarrage de l'infrastructure
Dans le dossier du projet, lancez :
```bash
docker compose up --build -d
```
> Le premier lancement télécharge les images officielles et construit l'image Jupyter contenant PySpark, Java et les dépendances nécessaires.

### 3. Tableau de bord des Services et Identifiants

| Service | URL locale | Identifiants |
| :--- | :--- | :--- |
| **JupyterLab** | [http://localhost:8888](http://localhost:8888) | Token : `medallion` |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | User : `admin` / Password : `password123` |
| **Metabase (BI)** | [http://localhost:3000](http://localhost:3000) | Compte à créer au premier accès (voir Notebook 04) |
| **PostgreSQL** | `localhost:5432` | DB : `gold_db`, User : `postgres`, Pwd : `postgres123` |

---

## 📚 Parcours Pédagogique des Notebooks

Les élèves ouvrent **JupyterLab** à l'adresse `http://localhost:8888` (mot de passe / token : `medallion`) et parcourent les notebooks dans l'ordre :

### 0️⃣ `00_architecture_et_connexions.ipynb`
- **Théorie** : Pourquoi l'architecture Médaillon a-t-elle émergé face aux limites des Data Lakes traditionnels ("Data Swamps") ?
- **Tests d'infrastructure** : Validation des connexions vers MinIO (boto3), PostgreSQL (SQLAlchemy) et initialisation d'une session PySpark avec le connecteur `S3A`.
- **Test d'écriture S3A** : Écriture et relecture d'un premier fichier parquet sur le stockage S3 local.

### 1️⃣ `01_ingestion_bronze.ipynb`
- **Le rôle de la couche Bronze** : Landing zone brute, immutabilité, conservation de l'historique exact et auditabilité.
- **Ingestion massive** : Téléchargement du jeu de données officiel des taxis new-yorkais (**~3 millions de lignes**) et de la table dimensionnelle des zones depuis AWS S3 Open Data.
- **Stockage brut** : Transfert direct dans le bucket MinIO `bronze` (`raw_year=2024/raw_month=01/`).
- **Inspection sans altération** : Découverte du schéma brut et comptage des enregistrements avec PySpark.

### 2️⃣ `02_transformation_silver.ipynb`
- **Audit de qualité** : Mise en évidence des anomalies présentes dans les données réelles (montants négatifs, distances nulles facturées $50+, dates aberrantes, passagers nuls).
- **Pipeline de nettoyage** : Filtrage strict selon les règles métier validées.
- **Enrichissement (Feature Engineering)** : Calcul de la durée (`trip_duration_minutes`), de la vitesse moyenne (`speed_mph`) et du taux de pourboire (`tip_rate`).
- **Jointure géographique** : Intégration des arrondissements (Manhattan, Brooklyn, Queens...).
- **Persistance optimisée** : Écriture dans le bucket MinIO `silver` au format **Parquet compressé avec Snappy**, partitionné par date (`pickup_date=YYYY-MM-DD`).

### 3️⃣ `03_chargement_gold.ipynb`
- **Pourquoi basculer du Data Lake (MinIO) au Data Warehouse (PostgreSQL) ?** : Explication des notions de latence, concurrence d'accès des outils de BI et indexation B-Tree.
- **Modélisation dimensionnelle** :
  - Dimension `dim_zones` (référentiel des zones et boroughs).
  - Mart 1 : `agg_daily_taxi_metrics` (chiffre d'affaires, courses et pourboires par jour et par compagnie).
  - Mart 2 : `agg_hourly_demand` (analyse des heures de pointe et de la congestion du trafic).
  - Mart 3 : `agg_borough_flows` (matrice origine/destination des flux de passagers).
- **Chargement relationnel** : Insertion optimisée dans PostgreSQL et validation des index.

### 4️⃣ `04_exploration_et_metabase.ipynb`
- **Requêtes analytiques SQL avancées** : Utilisation de Window Functions SQL (`OVER()`) pour calculer des parts de marché et des rangs.
- **Guide de démarrage Metabase** : Instructions illustrées pour relier Metabase à PostgreSQL en 2 minutes.
- **Recettes de Visualisation BI** : Configuration d'un tableau de bord de direction (KPI cards, courbes d'évolution temporelle, heatmap des heures de pointe, répartition par arrondissement).
- **Projets et Défis d'évaluation pour les élèves**.

---

## 🛠️ Commandes Utiles de Maintenance

### Voir les logs en direct d'un conteneur
```bash
docker compose logs -f jupyter
docker compose logs -f minio
docker compose logs -f postgres
```

### Arrêter l'environnement
```bash
docker compose down
```

### Réinitialiser complètement l'environnement (effacer données et volumes pour recommencer à zéro)
```bash
docker compose down -v
```

---

## 💡 Idées de Travaux Pratiques & Défis pour les Étudiants

1. **Défi Ingestion Multi-Mois (Partitionnement)** :
   Modifier le notebook `01` pour ingérer les mois de janvier, février et mars 2024. Observer l'impact du partitionnement lors d'une requête filtrant sur une date précise dans la couche Silver.
2. **Défi Unification Multi-Sources** :
   Télécharger le dataset complémentaire des **Green Taxis** (taxis des quartiers extérieurs) et harmoniser son schéma dans la couche Silver avec celui des Yellow Taxis.
3. **Défi Corrélation Externe (Météo NOAA)** :
   Télécharger des données météorologiques ouvertes d'AWS (NOAA) pour la ville de New York et analyser l'impact des précipitations sur le prix moyen et le volume de courses.
4. **Défi Ingestion Incrémentale / CDC** :
   Adapter le pipeline pour qu'il n'insère que les nouveaux trajets d'un jour à l'autre au lieu de réécrire l'ensemble de la table Gold.
