# Arquitectura del Sistema

## 1. Arquitectura general (visión de ambas unidades)
                          ┌───────────────────────┐
                          │       Ciudadanos /        │
                          │   Funcionarios / Bodega   │
                          └────────────┬───────────────┘
                                        │ HTTP/HTTPS
                                        ▼
                          ┌───────────────────────┐
                          │     Proxy / Gateway       │
                          │  (Nginx — punto de         │
                          │   entrada único)           │
                          └────────────┬───────────────┘
                                        │
          ┌──────────────┬─────────────┼──────────────┬─────────────┐
          ▼              ▼              ▼              ▼             ▼
    ┌──────────┐  ┌────────────┐ ┌────────────┐ ┌───────────┐ ┌────────────┐
    │ Frontend │  │   Auth      │ │  Trámites   │ │  Bodega    │ │     IA      │
    │ (Portal) │  │  (JWT)      │ │             │ │            │ │  (Gemini)   │
    └──────────┘  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └──────┬──────┘
                          │              │              │               │
                          ▼              ▼              ▼               │
                   ┌──────────┐  ┌──────────┐  ┌──────────┐            │
                   │ db-auth   │  │db-tramites│  │ db-bodega │◄───────────┘
                   └──────────┘  └──────────┘  └──────────┘   (consulta inventario)

    Monitoreo transversal: Prometheus + Grafana
    Persistencia: volúmenes Docker independientes del ciclo de vida de contenedores

La arquitectura evolucionó desde la Unidad 1 (múltiples VMs físicas con
servicios desplegados directamente sobre el sistema operativo) hacia la
Unidad 2 (un solo host con servicios containerizados y orquestados con
Docker Compose), manteniendo los mismos principios de seguridad:
segmentación de redes, base de datos sin exposición directa a internet, y
un único punto de entrada público.

## 2. Arquitectura containerizada (Unidad 2)
Internet

│

│ Puerto 80

▼

┌─────────────────────────────────────────────────────────────────┐

│  VM única (GCP, e2-medium) — Docker Engine                          │

│                                                                       │

│   ┌─────────────────┐                                                │

│   │  nginx-gateway    │  red-gateway                                  │

│   │  (puerto 80)       │◄──────────────┐                              │

│   └────────┬───────────┘                │                              │

│            │                            │                              │

│   ┌────────┴──────────┬─────────┬───────┴────┬──────────┐             │

│   ▼                    ▼         ▼            ▼          ▼             │

│ servicio-   servicio-   servicio-  servicio-   servicio-              │

│ portal      auth        tramites   bodega x2   ia                    │

│ (red-       (red-auth,  (red-      (red-       (red-bodega,           │

│  gateway)    red-       tramites,   bodega,      red-gateway)          │

│              gateway)    red-        red-gateway)                     │

│                          gateway)                                     │

│   │             │             │           │            │              │

│   │             ▼             ▼           ▼            │              │

│   │         db-auth     db-tramites   db-bodega         │              │

│   │       (red-auth)  (red-tramites) (red-bodega)       │              │

│   │                                                       │              │

│   └───────────────────────────────────────────────────────┘ (JWT)     │

│                                                                          │

│   ┌─────────────────┐    ┌──────────────┐    ┌──────────────┐         │

│   │  nginx-exporter   │───►│  prometheus   │───►│   grafana     │         │

│   │  (red-monitoreo)  │    │ (red-monitoreo)│    │ (red-monitoreo)│         │

│   └─────────────────┘    └──────────────┘    └──────────────┘         │

│                                                                          │

└──────────────────────────────────────────────────────────────────────┘

│

│ HTTPS externo

▼

┌──────────────────┐

│   Gemini API       │

│  (Google Cloud)    │

└──────────────────┘

### Redes Docker

| Red             | Propósito                                          |
|------------------|------------------------------------------------------|
| `red-gateway`    | Comunicación entre Nginx y los microservicios          |
| `red-auth`       | Aislamiento de `servicio-auth` con su base de datos    |
| `red-tramites`   | Aislamiento de `servicio-tramites` con su base de datos|
| `red-bodega`     | Aislamiento de `servicio-bodega`/`servicio-ia` con su BD|
| `red-monitoreo`  | Comunicación entre Prometheus, Grafana y nginx-exporter |

Ninguna base de datos está conectada a `red-gateway`; solo se accede a través
de su microservicio correspondiente, replicando el principio de aislamiento
de la Unidad 1 (donde la BD estaba en una VM separada sin IP pública).

## 3. Flujo entre servicios principales

### Flujo de autenticación
Usuario → Portal → servicio-auth (JWT) → db-auth

│

▼

JWT guardado en sesión Django del Portal

### Flujo de trámite ciudadano
Usuario → Portal → servicio-tramites (valida JWT) → db-tramites

### Flujo de gestión de bodega
Usuario (bodeguero) → Portal → servicio-bodega (valida JWT) → db-bodega

### Flujo del componente de IA
Usuario (bodeguero) → Portal → servicio-ia (valida JWT y rol)

│

├──► servicio-bodega (consulta inventario, propaga JWT)

│

└──► Gemini API (genera análisis)

│

▼

Respuesta renderizada en el Portal

Ver detalle completo en `docs/COMPONENTE_IA.md`.

## 4. Tecnologías utilizadas y justificación

| Tecnología              | Uso                                | Justificación                                                        |
|---------------------------|--------------------------------------|--------------------------------------------------------------------------|
| Django + DRF              | Todos los microservicios              | Framework maduro, rápido de desarrollar, ya usado en la Unidad 1         |
| PostgreSQL                | Persistencia de cada microservicio    | Robusto, relacional, usado también en la Unidad 1 (continuidad)         |
| JWT (`djangorestframework-simplejwt`) | Autenticación entre servicios | Permite autenticación stateless compartida entre microservicios          |
| Docker / Docker Compose   | Containerización y orquestación       | Exigido por el enunciado; facilita despliegue reproducible               |
| Nginx                     | Proxy inverso / gateway único         | Mismo rol que cumplía en la Unidad 1; punto único de entrada             |
| Gunicorn                  | Servidor WSGI de producción           | Reemplaza el servidor de desarrollo de Django (`runserver`)              |
| Prometheus + Grafana      | Monitoreo de infraestructura          | Estándar de la industria, visualización en tiempo real                   |
| Google Gemini API         | Componente de IA (análisis de inventario) | Costo más bajo y menor uso de recursos que un modelo local (Ollama), adecuado para el presupuesto de la VM (`e2-medium`, 4 GB RAM) |

## 5. Procedimiento de despliegue

Ver instrucciones completas en `README.md`, sección "Puesta en marcha".

Resumen:

```bash
git clone <repositorio>
cd proyecto
cp .env.example .env
nano .env   # completar credenciales y GEMINI_API_KEY
docker compose build
docker compose up -d
docker compose restart nginx   # refresca DNS interno tras el primer build
```

## 6. Monitoreo, respaldo y recuperación

Ver documentos dedicados:
- `docs/BACKUP_RESTORE.md` — sistema de respaldos de la Unidad 2
- `docs/ALTA_DISPONIBILIDAD.md` — resiliencia, múltiples instancias y recuperación ante fallos
- Sección "Monitoreo" en `README.md` — Prometheus + Grafana

## 7. Componente de IA

Ver `docs/COMPONENTE_IA.md` para el detalle completo del asistente de análisis
de inventario basado en Gemini.
