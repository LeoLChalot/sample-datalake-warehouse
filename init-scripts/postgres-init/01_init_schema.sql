-- Initialisation de la couche Gold (Data Warehouse)
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur PostgreSQL

CREATE SCHEMA IF NOT EXISTS gold;

-- 1. Table dimensionnelle des zones de New York (Boroughs & Quartiers)
CREATE TABLE IF NOT EXISTS gold.dim_zones (
    location_id INT PRIMARY KEY,
    borough VARCHAR(50),
    zone_name VARCHAR(100),
    service_zone VARCHAR(50)
);

-- 2. Table de faits agrégée : Métriques quotidiennes par arrondissement et opérateur
CREATE TABLE IF NOT EXISTS gold.agg_daily_taxi_metrics (
    id SERIAL PRIMARY KEY,
    pickup_date DATE NOT NULL,
    borough VARCHAR(50) NOT NULL,
    vendor_id INT,
    total_trips INT NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    total_fare NUMERIC(12, 2) NOT NULL,
    total_tips NUMERIC(12, 2) NOT NULL,
    avg_trip_distance NUMERIC(8, 2),
    avg_trip_duration_min NUMERIC(8, 2),
    avg_tip_rate NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON gold.agg_daily_taxi_metrics(pickup_date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_borough ON gold.agg_daily_taxi_metrics(borough);

-- 3. Table de faits agrégée : Analyse de la demande horaire et vitesse moyenne
CREATE TABLE IF NOT EXISTS gold.agg_hourly_demand (
    pickup_hour INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    total_trips INT NOT NULL,
    avg_duration_min NUMERIC(8, 2),
    avg_speed_mph NUMERIC(8, 2),
    total_revenue NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY (pickup_hour, day_of_week)
);

-- 4. Table de faits agrégée : Matrice des flux entre arrondissements (Origine -> Destination)
CREATE TABLE IF NOT EXISTS gold.agg_borough_flows (
    pickup_borough VARCHAR(50) NOT NULL,
    dropoff_borough VARCHAR(50) NOT NULL,
    total_trips INT NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    avg_duration_min NUMERIC(8, 2),
    PRIMARY KEY (pickup_borough, dropoff_borough)
);

-- Vue d'accès rapide pour Metabase
CREATE OR REPLACE VIEW gold.v_top_performing_boroughs AS
SELECT 
    borough,
    SUM(total_trips) as total_rides,
    SUM(total_revenue) as gross_revenue,
    ROUND(AVG(avg_trip_distance), 2) as overall_avg_distance,
    ROUND(AVG(avg_tip_rate) * 100, 2) as avg_tip_percentage
FROM gold.agg_daily_taxi_metrics
GROUP BY borough
ORDER BY gross_revenue DESC;
