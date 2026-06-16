# Alta Disponibilidad y Resiliencia

## Estrategia implementada

La solución implementa resiliencia en 4 niveles:

### 1. Múltiples instancias de servicios críticos

El servicio `servicio-bodega` corre con 2 instancias simultáneas:

```bash
docker compose up -d --scale servicio-bodega=2
```

Evidencia (ver `docs/evidencias/alta_disponibilidad.txt`):
proyecto-servicio-bodega-1   Up 5 hours (healthy)

proyecto-servicio-bodega-2   Up 15 seconds (healthy)

### 2. Balanceo de tráfico

Nginx actúa como gateway único con un upstream hacia `servicio-bodega:8000`.
Docker DNS resuelve automáticamente ese nombre a las IPs de ambas instancias
y distribuye el tráfico entre ellas con round-robin sin configuración adicional.

```nginx
upstream bodega_service {
    server servicio-bodega:8000;  # Docker DNS resuelve a ambas instancias
}
```

### 3. Recuperación ante caída de contenedores

Todos los servicios tienen `restart: unless-stopped`. Ante una caída, Docker
reinicia el contenedor automáticamente sin intervención manual.

Evidencia de prueba (ver `docs/evidencias/alta_disponibilidad.txt`):
- Estado inicial: todos los servicios `healthy`
- `servicio-bodega` detenido: contenedor desaparece de `docker compose ps`
- Tras `docker compose up -d`: contenedor reiniciado en 40 segundos, `healthy`

Además, todos los servicios tienen `HEALTHCHECK` configurado, lo que permite
a Docker detectar contenedores en mal estado y reiniciarlos.

### 4. Persistencia desacoplada del ciclo de vida de los contenedores

Los datos están almacenados en volúmenes Docker nombrados, independientes
del ciclo de vida de los contenedores:

| Volumen                  | Servicio    | Contenido               |
|--------------------------|-------------|-------------------------|
| `proyecto_db_auth_data`  | db-auth     | Usuarios y credenciales |
| `proyecto_db_tramites_data` | db-tramites | Trámites municipales |
| `proyecto_db_bodega_data` | db-bodega  | Inventario y solicitudes|
| `proyecto_prometheus_data` | prometheus | Métricas históricas    |
| `proyecto_grafana_data`  | grafana     | Dashboards y config     |

Al eliminar y recrear cualquier contenedor, los datos persisten intactos
en el volumen correspondiente.

## Comandos útiles

```bash
# Escalar servicio-bodega a 2 instancias
docker compose up -d --scale servicio-bodega=2

# Ver estado de todas las instancias
docker compose ps

# Verificar recuperación ante caída
docker compose stop servicio-bodega
docker compose up -d servicio-bodega
docker compose ps servicio-bodega
```
