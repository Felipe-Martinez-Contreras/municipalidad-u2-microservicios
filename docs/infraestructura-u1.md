# Infraestructura de la Unidad 1

## Descripción general

La Unidad 1 desplegó la plataforma sobre Google Cloud Platform (GCP) usando
máquinas virtuales independientes (sin contenedores), separando las capas de
proxy, aplicación y base de datos en distintas VMs dentro de una red privada
segmentada.

## Topología de VMs

| VM             | IP            | Tipo     | Rol                                          |
|-----------------|---------------|----------|-----------------------------------------------|
| `vm-nginx`      | 34.176.156.84 | Pública  | Nginx: proxy inverso y balanceador de carga   |
| `vm-app-db`     | 10.0.2.2      | Privada  | Backend Django (nodo 1)                       |
| `vm-app-db-2`   | 10.0.2.4      | Privada  | Backend Django (nodo 2, clon vía snapshot)    |
| `vm-db`         | 10.0.2.3      | Privada  | Base de datos PostgreSQL                      |

## Diagrama de flujo
Internet
                   │
                   │ HTTP/HTTPS (80/443)
                   ▼
          ┌─────────────────┐
          │    vm-nginx      │  IP pública: 34.176.156.84
          │  (proxy inverso  │
          │  + balanceador)  │
          └────────┬─────────┘
                    │ round-robin
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐

│   vm-app-db      │    │  vm-app-db-2      │

│  10.0.2.2:8000   │    │  10.0.2.4:8000     │

│  Django (nodo 1) │    │  Django (nodo 2)   │

└────────┬──────────┘    └─────────┬──────────┘

│                          │

└────────────┬─────────────┘

▼

┌──────────────────┐

│     vm-db          │

│  10.0.2.3:5432      │

│  PostgreSQL          │

│  municipalidad_db    │

└──────────────────┘
Todas las VMs de aplicación y BD están en red privada,

sin IP pública. Solo vm-nginx es accesible desde internet.

## Justificación de decisiones técnicas

- **Separación pública/privada**: solo `vm-nginx` tiene IP pública, lo que reduce
  la superficie de ataque y protege los servicios críticos (aplicación y BD).
- **Base de datos aislada**: PostgreSQL corre en una VM dedicada (`vm-db`),
  protegiendo los datos ante eventuales caídas o intervenciones en las VMs de
  aplicación.
- **Dos nodos de backend**: implementan alta disponibilidad mediante balanceo de
  carga. Si un nodo cae, Nginx redirige el tráfico al nodo restante.
- **Aprovisionamiento por snapshot**: `vm-app-db-2` fue creada a partir de un
  snapshot de `vm-app-db`, garantizando una configuración idéntica entre ambos
  nodos de backend.

## Servicios configurados

### Nginx — Proxy inverso y balanceador de carga

Configuración (`/etc/nginx/sites-enabled/municipalidad`):

```nginx
upstream backend {
    server 10.0.2.2:8000;
    server 10.0.2.4:8000;
}

server {
    listen 80;
    server_name 34.176.156.84;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Django — Aplicación web

- Framework: Django 5.2, Python 3.12 (entorno virtual)
- Módulos: `portal`, `tramites`, `bodega`, `usuarios`, `administracion`
- Configuración de base de datos (`settings.py`):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'municipalidad_db',
        'USER': 'municipalidad_user',
        'HOST': '10.0.2.3',
        'PORT': '5432',
    }
}
```

### PostgreSQL — Base de datos

- Versión: PostgreSQL 16
- VM dedicada: `vm-db` (10.0.2.3)
- Base de datos: `municipalidad_db`
- Usuario: `municipalidad_user`
- Acceso permitido únicamente desde `10.0.2.2` y `10.0.2.4` (configurado en
  `pg_hba.conf`)

### Monitoreo

- Prometheus: `http://34.176.156.84/prometheus/`
- Grafana: `http://34.176.156.84/grafana/`

## Acceso remoto (SSH)

Todas las VMs son accesibles mediante SSH con llave pública. Las VMs privadas
se acceden únicamente a través de `vm-nginx` (salto/jump host):

```bash
# Acceso a vm-nginx (pública)
ssh usuario@34.176.156.84

# Acceso a VMs privadas, desde vm-nginx
ssh usuario@10.0.2.2   # vm-app-db
ssh usuario@10.0.2.4   # vm-app-db-2
ssh usuario@10.0.2.3   # vm-db
```

## Backup y restauración (Unidad 1)

### Crear backup

Ejecutar en `vm-db`:

```bash
sudo -u postgres pg_dump municipalidad_db > ~/backup_municipalidad.sql
```

### Procedimiento de restauración

En caso de pérdida o corrupción de la base de datos, ejecutar en `vm-db`:

```bash
# Paso 1: Recrear la base de datos
sudo -u postgres psql -c "DROP DATABASE IF EXISTS municipalidad_db;"
sudo -u postgres createdb municipalidad_db

# Paso 2: Otorgar permisos
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE municipalidad_db TO municipalidad_user;"
sudo -u postgres psql -d municipalidad_db -c "GRANT ALL ON SCHEMA public TO municipalidad_user;"

# Paso 3: Restaurar datos
sudo -u postgres psql municipalidad_db < ~/backup_municipalidad.sql

# Paso 4: Aplicar migraciones (en vm-app-db)
cd ~/municipalidad_web
source ~/municipalidad/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Ubicación de backups

- Backup primario: `vm-db` → `~/backup_municipalidad.sql`
- Backup secundario: `vm-app-db` (copia del backup original)

Ambas VMs en red privada para mayor seguridad.

## Evolución hacia la Unidad 2

Esta infraestructura de múltiples VMs fue la base sobre la cual se diseñó la
arquitectura containerizada de la Unidad 2 (ver `docs/arquitectura.md`). Los
mismos conceptos de segmentación de red, balanceo de carga y aislamiento de
base de datos se mantuvieron, pero migrados de VMs físicas separadas a redes
Docker internas dentro de una única VM (`e2-medium`), reduciendo costos de
infraestructura sin perder los principios de seguridad y resiliencia.

> Nota: la IP pública `34.176.156.84` de la Unidad 1 corresponde a una VM que
> ya no está activa (recursos liberados tras avanzar a la Unidad 2).
