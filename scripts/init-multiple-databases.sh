#!/bin/bash
# ============================================================
# Initialize multiple databases in the shared Postgres instance
# Each service (n8n, Dify, Postiz, Crew) gets its own database
# ============================================================

set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating databases for n8n, dify, postiz, crew..."

$POSTGRES <<-EOSQL
    CREATE DATABASE n8n;
    CREATE DATABASE dify;
    CREATE DATABASE postiz;
    CREATE DATABASE crew;
    GRANT ALL PRIVILEGES ON DATABASE n8n TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON DATABASE dify TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON DATABASE postiz TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON DATABASE crew TO ${POSTGRES_USER};
EOSQL

echo "Databases created successfully."
