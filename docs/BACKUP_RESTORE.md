# Sistema de Backups y Restauración

## 1. Descripción

El sistema cuenta con scripts para respaldar y restaurar las 3 bases de datos
PostgreSQL del proyecto (`db-auth`, `db-tramites`, `db-bodega`) mediante `pg_dump`
y `pg_restore`/`psql`.

Ubicación:
- Backup: `scripts/backup/backup.sh`
- Restore: `scripts/restore/restore.sh`
- Archivos generados: `scripts/backup/backups/`

## 2. Cómo hacer un backup

Con todos los contenedores de base de datos en ejecución (`db-auth`, `db-tramites`,
`db-bodega`):

```bash
cd scripts/backup
./backup.sh
```

Esto genera 3 archivos `.sql` con timestamp, por ejemplo:
backups/auth_20260615_024503.sql

backups/tramites_20260615_024503.sql

backups/bodega_20260615_024503.sql

Cada dump usa `pg_dump --clean --if-exists`, por lo que el archivo incluye los
comandos necesarios para limpiar las tablas existentes antes de recrearlas.

## 3. Cómo restaurar un backup

```bash
cd scripts/restore
./restore.sh YYYYMMDD_HHMMSS
```

Donde `YYYYMMDD_HHMMSS` es el timestamp del backup a restaurar (debe coincidir
en los 3 archivos `.sql`). Si se ejecuta sin argumentos, el script lista los
timestamps disponibles.
cat > docs/BACKUP_RESTORE.md << 'EOF'
# Sistema de Backups y Restauración

## 1. Descripción

El sistema cuenta con scripts para respaldar y restaurar las 3 bases de datos
PostgreSQL del proyecto (`db-auth`, `db-tramites`, `db-bodega`) mediante `pg_dump`
y `pg_restore`/`psql`.

Ubicación:
- Backup: `scripts/backup/backup.sh`
- Restore: `scripts/restore/restore.sh`
- Archivos generados: `scripts/backup/backups/`

## 2. Cómo hacer un backup

Con todos los contenedores de base de datos en ejecución (`db-auth`, `db-tramites`,
`db-bodega`):

```bash
cd scripts/backup
./backup.sh
```

Esto genera 3 archivos `.sql` con timestamp, por ejemplo:
backups/auth_20260615_024503.sql

backups/tramites_20260615_024503.sql

backups/bodega_20260615_024503.sql

Cada dump usa `pg_dump --clean --if-exists`, por lo que el archivo incluye los
comandos necesarios para limpiar las tablas existentes antes de recrearlas.

## 3. Cómo restaurar un backup

```bash
cd scripts/restore
./restore.sh YYYYMMDD_HHMMSS
```

Donde `YYYYMMDD_HHMMSS` es el timestamp del backup a restaurar (debe coincidir
en los 3 archivos `.sql`). Si se ejecuta sin argumentos, el script list
El script pedirá confirmación antes de sobrescribir los datos actuales:
⚠️  ADVERTENCIA: Esto sobreescribirá los datos actuales.

¿Continuar? (s/N):

## 4. Recomendaciones de uso

- Ejecutar `backup.sh` antes de cualquier cambio mayor (migraciones, actualizaciones
  de versión, pruebas destructivas).
- Los archivos `.sql` generados **no deben subirse al repositorio** (agregar
  `scripts/backup/backups/*.sql` a `.gitignore` si no está ya).
- Para automatizar backups periódicos, se puede agregar una entrada `cron`, por ejemplo:
0 2 * * * /home/fmart/proyecto/scripts/backup/backup.sh >> /home/fmart/proyecto/scripts/backup/backup.log 2>&1

## 5. Evidencia de prueba

Se ejecutó el script de backup exitosamente sobre las 3 bases de datos con datos
reales del sistema en producción (ver archivos `.sql` generados con timestamps
`20260615_024503` y `20260615_024621` en `scripts/backup/backups/`).
