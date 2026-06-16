# Portal Municipal La Estrella — Sistema de Gestión Municipal

Sistema de gestión municipal basado en arquitectura de microservicios containerizados con Docker y Docker Compose.

## Arquitectura
┌─────────────────┐
                     │  Nginx Gateway   │  :80
                     └────────┬─────────┘
                               │
    ┌──────────────┬──────────┼──────────────┬─────────────┐
    │               │          │               │             │
## Servicios

| Servicio            | Descripción                                    | Puerto interno |
|---------------------|------------------------------------------------|----------------|
| `servicio-auth`     | Autenticación y gestión de usuarios (JWT)      | 8000           |
| `servicio-tramites` | Gestión de trámites municipales                 | 8000           |
| `servicio-bodega`   | Control de inventario y solicitudes de bodega   | 8000           |
| `servicio-ia`       | Análisis de inventario con IA (Gemini)          | 8000           |
| `servicio-portal`   | Frontend web (Django)                           | 8000           |
| `db-auth`           | PostgreSQL — datos de autenticación            | 5432           |
| `db-tramites`       | PostgreSQL — datos de trámites                  | 5432           |
| `db-bodega`         | PostgreSQL — datos de bodega                    | 5432           |
| `nginx`             | Gateway / proxy reverso                         | 80             |
| `prometheus`        | Recolección de métricas                         | 9090           |
| `grafana`           | Visualización de métricas                       | 3000           |

## Requisitos previos

- Docker y Docker Compose instalados
- Archivo `.env` configurado (ver `.env.example`)

## Puesta en marcha

```bash
# 1. Copiar y completar variables de entorno
cp .env.example .env
nano .env   # completar contraseñas, claves secretas y GEMINI_API_KEY

# 2. Construir e iniciar todos los servicios
docker compose build
docker compose up -d

# 3. Verificar estado
docker compose ps
```

Accesos:
- Portal web: `http://<IP_SERVIDOR>/`
- Grafana: `http://<IP_SERVIDOR>:3000` (usuario/clave en `.env`)
- Prometheus: `http://<IP_SERVIDOR>:9090` (solo red interna por defecto)

## Roles del sistema

| Rol          | Descripción                                  |
|--------------|-----------------------------------------------|
| `ciudadano`  | Puede crear y dar seguimiento a trámites      |
| `funcionario`| Gestiona trámites y solicitudes de bodega     |
| `bodeguero`  | Gestiona inventario, solicitudes y análisis IA|
| `jefatura`   | Aprueba solicitudes, supervisión              |
| `admin`      | Acceso completo                                |

## Notas operativas importantes

- **Tras reconstruir cualquier servicio** (`docker compose build <servicio> && docker compose up -d`), reiniciar nginx para refrescar su caché DNS interna:
```bash
  docker compose restart nginx
```
- Todos los contenedores de aplicación corren con usuario no privilegiado (`appuser`).
- Todos los servicios críticos cuentan con `HEALTHCHECK` y política `restart: unless-stopped`.

## Documentación adicional

- [Componente de IA — Análisis de Inventario](docs/COMPONENTE_IA.md)
- [Sistema de Backups y Restauración](docs/BACKUP_RESTORE.md)

## Créditos

Proyecto desarrollado para Municipalidad La Estrella — Proyecto Integrado U1 + U2, Administración de Redes, Universidad de Talca - ICC.
- [Alta Disponibilidad y Resiliencia](docs/ALTA_DISPONIBILIDAD.md)

## Presupuesto y Cotización (5.10)

### 1. Costos de Desarrollo

| Ítem                              | Horas | Valor hora (CLP) | Total (CLP)   |
|-----------------------------------|-------|------------------|---------------|
| Diseño de arquitectura            | 8     | $15.000          | $120.000      |
| Desarrollo microservicios (5)     | 40    | $15.000          | $600.000      |
| Containerización y Docker Compose | 12    | $15.000          | $180.000      |
| Integración IA (Gemini)           | 8     | $15.000          | $120.000      |
| Configuración monitoreo           | 6     | $15.000          | $90.000       |
| Sistema de backups                | 4     | $15.000          | $60.000       |
| Documentación y pruebas           | 6     | $15.000          | $90.000       |
| **Total desarrollo**              | **84**| -                | **$1.260.000**|

> Desarrollado por 1 persona durante 6 semanas (Unidades 1 y 2).

---

### 2. Costos de Infraestructura (GCP — mensual)

| Recurso                              | Especificación         | Costo mensual (USD) |
|--------------------------------------|------------------------|---------------------|
| VM Compute Engine (`e2-medium`)      | 2 vCPU, 4 GB RAM       | ~$26.11             |
| Disco persistente (boot, 10 GB SSD)  | pd-balanced            | ~$1.70              |
| Transferencia de datos saliente      | ~10 GB/mes estimado    | ~$1.20              |
| IP externa estática                  | 1 IP                   | ~$3.65              |
| **Total infraestructura mensual**    |                        | **~$32.66 USD**     |
| **Total infraestructura anual**      |                        | **~$391.92 USD**    |

> Equivalente aproximado en CLP (USD × $950): **~$372.300 CLP/año**

---

### 3. Costos de Operación y Mantención (anual)

| Ítem                                      | Frecuencia   | Costo estimado (CLP) |
|-------------------------------------------|--------------|----------------------|
| Mantención y actualizaciones del sistema  | Mensual (4h) | $720.000/año         |
| Monitoreo y respuesta a incidentes        | Mensual (2h) | $360.000/año         |
| Renovación de dominio (si aplica)         | Anual        | $15.000/año          |
| Respaldos externos (Google Cloud Storage) | Mensual      | ~$12.000/año         |
| **Total operación anual**                 |              | **$1.107.000/año**   |

---

### 4. Costos Asociados al Componente de IA (Gemini)

| Modelo             | Uso estimado         | Costo por solicitud | Costo mensual estimado |
|--------------------|----------------------|---------------------|------------------------|
| `gemini-2.0-flash` | ~200 análisis/mes    | ~$0.000075 USD      | ~$0.015 USD            |

> El modelo Gemini 2.0 Flash tiene una capa gratuita de **1.500 solicitudes/día**,
> por lo que para el volumen de uso de una municipalidad pequeña el costo operacional
> de IA es **$0 USD/mes** dentro del free tier de Google AI Studio.

---

### Resumen General

| Categoría                     | Costo estimado (CLP)     |
|-------------------------------|--------------------------|
| Desarrollo (único)            | $1.260.000               |
| Infraestructura (año 1)       | $372.300                 |
| Operación y mantención (año 1)| $1.107.000               |
| Componente IA (año 1)         | $0 (free tier)           |
| **Total año 1**               | **$2.739.300**           |
| **Total año 2 en adelante**   | **$1.479.300/año**       |

> Los costos de infraestructura pueden reducirse usando instancias `e2-small`
> (~$13 USD/mes) si el tráfico lo permite, o usando el crédito gratuito de GCP
> ($300 USD para nuevas cuentas).
