-- Runs once, the first time the Postgres volume is created.
-- Airflow keeps its own metadata in a separate database.
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
