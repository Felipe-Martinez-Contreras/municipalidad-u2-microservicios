#!/bin/bash
# ============================================================
# Script de Restore - Portal Municipal La Estrella
# Restaura las 3 bases de datos desde un backup
# Uso: ./restore.sh 20240614_120000
# ============================================================

set -e

if [ -z "$1" ]; then
    echo "❌ Error: debes indicar la fecha del backup."
    echo "   Uso: ./restore.sh YYYYMMDD_HHMMSS"
    echo ""
    echo "   Backups disponibles:"
    ls "$(dirname "$0")/../backup/backups/"*.sql 2>/dev/null | sed 's/.*_\([0-9]*_[0-9]*\)\.sql/   \1/' | sort -u
    exit 1
fi

FECHA=$1
BACKUP_DIR="$(dirname "$0")/../backup/backups"

echo "=================================================="
echo " Restore Municipal - Fecha: $FECHA"
echo "=================================================="

# Verificar que existen los archivos
for DB in auth tramites bodega; do
    if [ ! -f "$BACKUP_DIR/${DB}_${FECHA}.sql" ]; then
        echo "❌ No se encontró: ${DB}_${FECHA}.sql"
        exit 1
    fi
done

echo "⚠️  ADVERTENCIA: Esto sobreescribirá los datos actuales."
read -p "¿Continuar? (s/N): " confirm
if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo "Cancelado."
    exit 0
fi

# ── AUTH ──────────────────────────────────────────────────
echo "[1/3] Restaurando db-auth..."
docker exec -i db-auth psql -U auth_user -d auth_db < "$BACKUP_DIR/auth_${FECHA}.sql"
echo "      ✅ db-auth restaurada"

# ── TRÁMITES ──────────────────────────────────────────────
echo "[2/3] Restaurando db-tramites..."
docker exec -i db-tramites psql -U tramites_user -d tramites_db < "$BACKUP_DIR/tramites_${FECHA}.sql"
echo "      ✅ db-tramites restaurada"

# ── BODEGA ────────────────────────────────────────────────
echo "[3/3] Restaurando db-bodega..."
docker exec -i db-bodega psql -U bodega_user -d bodega_db < "$BACKUP_DIR/bodega_${FECHA}.sql"
echo "      ✅ db-bodega restaurada"

echo ""
echo "=================================================="
echo " Restore completado exitosamente."
echo "=================================================="
