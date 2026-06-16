# Licitación — Desarrollo de Plataforma Web para la Gestión de Fomento Productivo

## Información general

- **Código licitación (Mercado Público)**: 4768-28-LE26
- **Responsable**: I. Municipalidad de La Estrella
- **Enlace**: https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?qs=uDdWCmVgJq44CwfEuPMTeQ==

## Descripción del problema

La Municipalidad de La Estrella carecía de herramientas digitales para la gestión
eficiente de sus procesos internos y de atención ciudadana. No existía una plataforma
unificada que permitiera a los ciudadanos realizar trámites en línea ni hacer
seguimiento de sus solicitudes. Internamente, la gestión de bodega (inventario,
solicitudes por unidad municipal, flujos de aprobación) se realizaba de forma manual
y sin trazabilidad.

## Actores principales

| Actor                                | Rol en el sistema                                                  |
|---------------------------------------|----------------------------------------------------------------------|
| Ciudadanos                            | Realizan trámites en línea y consultan estado de solicitudes        |
| Funcionarios municipales (DIDECO, OMIL) | Revisan y gestionan trámites de su competencia                    |
| Encargado de bodega                   | Control de inventario, aprobación de solicitudes internas           |
| Funcionarios de Salud y Educación     | Solicitan productos a bodega, consultan disponibilidad              |
| Jefatura / Supervisores               | Visualizan stock crítico y trámites en curso                        |
| Unidad Técnica / Informática          | Administra servidor, backups, firewall y soporte                    |

## Módulos requeridos por las bases técnicas

1. **Formularios web inteligentes**: campos dinámicos, adjuntar documentos,
   validación automática, número de solicitud automático, notificaciones por correo,
   exportación a Excel, panel de seguimiento.
2. **Plataforma de trámites en línea**: registro de usuarios, seguimiento de estado
   en tiempo real, panel administrativo por departamento, reportes mensuales.
3. **Sistema de control de bodega**: inventario, ingreso/salida de productos,
   solicitudes internas con flujo de aprobación, alertas de stock mínimo, reportes
   por área, historial de movimientos.
4. **Seguridad informática**: SSL, WAF, backups diarios, acceso SSH solo con llave
   pública.
5. **Servidor de alta disponibilidad**: recursos garantizados, uptime ≥99,9%.

## Requisitos no funcionales clave

- Acceso administrativo exclusivamente vía SSH con llave pública (sin contraseña).
- Base de datos en red privada, sin acceso directo desde internet.
- Backups diarios con retención mínima de 30 días, en ubicación separada del
  servidor principal.
- Código versionado en repositorio Git.
- Para la Unidad 2: containerización con Docker y Docker Compose, con volúmenes
  persistentes para permitir escalar módulos de forma independiente.

## Cómo el proyecto entregado responde a la licitación

| Requisito de la licitación                          | Implementación en este proyecto                              |
|--------------------------------------------------------|------------------------------------------------------------------|
| Plataforma de trámites en línea                       | `servicio-tramites` (Django + DRF)                              |
| Sistema de control de bodega                          | `servicio-bodega` (Django + DRF)                                |
| Acceso/autenticación de usuarios                       | `servicio-auth` (JWT)                                            |
| Frontend / panel ciudadano y administrativo            | `servicio-portal` (Django + Bootstrap)                          |
| Asistente de IA para apoyo en gestión                  | `servicio-ia` (análisis de inventario con Gemini)               |
| Proxy inverso / punto de entrada único                 | Nginx (`infrastructure/proxy`)                                  |
| Monitoreo de disponibilidad                            | Prometheus + Grafana (`infrastructure/monitoring`)               |
| Backups diarios con procedimiento documentado           | `scripts/backup/`, `scripts/restore/`, `docs/BACKUP_RESTORE.md` |
| Base de datos aislada / sin exposición directa          | 3 bases PostgreSQL en redes Docker internas, sin puertos públicos |
| Containerización (Unidad 2)                            | Docker + Docker Compose, ver `docs/arquitectura.md`              |

> Nota: la licitación original sugería Ollama como motor de IA local; el equipo
> optó por la API de Gemini por su menor costo operativo (capa gratuita amplia)
> y menor requerimiento de recursos en la VM, dado el presupuesto académico
> disponible (ver `docs/presupuesto.md`).
