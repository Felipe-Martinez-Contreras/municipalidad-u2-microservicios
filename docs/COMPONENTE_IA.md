# Componente de Inteligencia Artificial — Análisis de Inventario

## 1. Problema que resuelve

El servicio `servicio-ia` agrega un asistente de análisis de inventario que ayuda al
personal de bodega a tomar decisiones de reposición y gestión de stock. En lugar de
revisar manualmente cada producto, el sistema entrega un análisis automático generado
por IA con recomendaciones concretas sobre:

- productos con stock bajo o en cero que requieren reposición prioritaria;
- productos con exceso de stock que inmovilizan capital;
- observaciones generales sobre la gestión del inventario.

## 2. Tecnología utilizada

- **Modelo**: Google Gemini (`gemini-2.0-flash`, configurable vía `GEMINI_MODEL`)
- **Framework del servicio**: Django + Django REST Framework
- **Autenticación**: JWT compartido con el resto de los microservicios

## 3. Integración al flujo del sistema
Usuario (bodeguero/jefatura/admin)

│

│ 1. Inicia sesión en el Portal (JWT guardado en sesión Django)

▼

Portal (servicio-portal)

│

│ 2. Click en "Análisis IA" en /portal/bodega/

│    GET /portal/bodega/analisis-ia/

▼

servicio-ia (/ai/analisis-inventario/)

│

│ 3. Valida rol del usuario (bodeguero, jefatura, admin)

│ 4. Solicita inventario actual, propagando el JWT del usuario

▼

servicio-bodega (/bodega/inventario/)

│

│ 5. Devuelve listado de productos (stock actual, mínimo, etc.)

▼

servicio-ia

│

│ 6. Construye un prompt en español con el inventario

│ 7. Llama a la API de Gemini

▼

Gemini API

│

│ 8. Devuelve análisis y recomendaciones en texto

▼

servicio-ia → Portal → Usuario (tarjeta con recomendaciones)

## 4. Endpoint

**Ruta pública (vía gateway nginx):**
GET /api/ai/analisis-inventario/

Authorization: Bearer <JWT>

**Ruta interna (vía portal, sesión Django):**
GET /portal/bodega/analisis-ia/
(no requiere pasar el token manualmente; el portal lo toma de la sesión)

### Roles permitidos
`bodeguero`, `jefatura`, `admin`

### Respuesta exitosa (200)
```json
{
  "total_productos": 3,
  "analisis": "Aquí están las recomendaciones:\n\n*   **1. Prioridad de Reposición:** ..."
}
```

### Respuestas de error
| Código | Causa                                              |
|--------|-----------------------------------------------------|
| 401    | Token inválido o no enviado                        |
| 403    | Usuario sin rol autorizado                          |
| 500    | `GEMINI_API_KEY` no configurada en el servidor      |
| 502    | Error al consultar `servicio-bodega` o Gemini API   |

## 5. Variables de entorno

| Variable            | Descripción                                  |
|---------------------|-----------------------------------------------|
| `GEMINI_API_KEY`    | Clave de API de Google Gemini                 |
| `GEMINI_MODEL`      | Modelo a usar (default: `gemini-2.0-flash`)   |
| `BODEGA_SERVICE_URL`| URL interna de `servicio-bodega`               |
| `AI_SECRET_KEY`     | Secret key de Django para `servicio-ia`        |
| `JWT_SECRET_KEY`    | Clave JWT compartida entre todos los servicios |

## 6. Cómo demostrarlo (defensa)

1. Iniciar sesión en el portal con un usuario de rol `bodeguero` (o `jefatura`/`admin`).
2. Ir a **Inventario** (`/portal/bodega/`).
3. Hacer clic en el botón **"Análisis IA"**.
4. El sistema consulta el inventario actual, lo envía a Gemini y muestra las
   recomendaciones en una tarjeta debajo de la tabla.

### Prueba vía línea de comandos

```bash
# 1. Obtener token
TOKEN=$(curl -s -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "bodeguero@municipalidad.cl", "password": "bode1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# 2. Solicitar análisis
curl -s http://localhost/api/ai/analisis-inventario/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 7. Evidencia de funcionamiento

Ver `docs/evidencias/logs_demo_ia.txt` para logs de una ejecución real exitosa
(respuesta HTTP 200, análisis generado por Gemini con 3 productos de inventario real).
