#!/bin/bash
# ============================================================
# Script de Backup - Portal Municipal La Estrella
# Hace pg_dump de las 3 bases de datos del sistema
# Uso: ./backup.sh
# ============================================================

set -e

BACKUP_DIR="$(dirname "$0")/backups"
FECHA=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "=================================================="
echo " Backup Municipal - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

# ── AUTH ──────────────────────────────────────────────────
echo "[1/3] Haciendo backup de db-auth..."
docker exec db-auth pg_dump -U auth_user --clean --if-exists auth_db > "$BACKUP_DIR/auth_${FECHA}.sql"
echo "      ✅ Guardado: auth_${FECHA}.sql"

# ── TRÁMITES ──────────────────────────────────────────────
echo "[2/3] Haciendo backup de db-tramites..."
docker exec db-tramites pg_dump -U tramites_user --clean --if-exists tramites_db > "$BACKUP_DIR/tramites_${FECHA}.sql"
echo "      ✅ Guardado: tramites_${FECHA}.sql"

# ── BODEGA ────────────────────────────────────────────────
echo "[3/3] Haciendo backup de db-bodega..."
docker exec db-bodega pg_dump -U bodega_user --clean --if-exists bodega_db > "$BACKUP_DIR/bodega_${FECHA}.sql"
echo "      ✅ Guardado: bodega_${FECHA}.sql"

echo ""
echo "=================================================="
echo " Backup completado: $FECHA"
echo " Archivos en: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"/*_${FECHA}.sql
echo "=================================================="
