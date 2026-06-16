# Presupuesto y Cotización

> Este documento contiene el detalle completo del análisis económico del
> proyecto. Un resumen también está disponible en `README.md`, sección
> "Presupuesto y Cotización".

## 1. Costos de Desarrollo

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

## 2. Costos de Infraestructura (GCP — mensual)

| Recurso                              | Especificación         | Costo mensual (USD) |
|--------------------------------------|------------------------|----------------------|
| VM Compute Engine (`e2-medium`)      | 2 vCPU, 4 GB RAM       | ~$26.11              |
| Disco persistente (boot, 10 GB SSD)  | pd-balanced            | ~$1.70               |
| Transferencia de datos saliente      | ~10 GB/mes estimado    | ~$1.20               |
| IP externa estática                  | 1 IP                   | ~$3.65               |
| **Total infraestructura mensual**    |                        | **~$32.66 USD**      |
| **Total infraestructura anual**      |                        | **~$391.92 USD**     |

> Equivalente aproximado en CLP (USD × $950): **~$372.300 CLP/año**

Esta configuración (`e2-medium`, una sola VM) reemplazó el diseño original de
la Unidad 1 (4 VMs separadas: `vm-nginx`, `vm-app-db`, `vm-app-db-2`, `vm-db`),
consolidando todos los servicios en contenedores dentro de un único host. Esto
redujo significativamente el costo mensual de infraestructura, manteniendo el
aislamiento de red mediante redes Docker en lugar de VMs físicas separadas.

## 3. Costos de Operación y Mantención (anual)

| Ítem                                      | Frecuencia   | Costo estimado (CLP) |
|--------------------------------------------|--------------|------------------------|
| Mantención y actualizaciones del sistema    | Mensual (4h) | $720.000/año           |
| Monitoreo y respuesta a incidentes          | Mensual (2h) | $360.000/año           |
| Renovación de dominio (si aplica)           | Anual        | $15.000/año            |
| Respaldos externos (Google Cloud Storage)   | Mensual      | ~$12.000/año           |
| **Total operación anual**                   |              | **$1.107.000/año**     |

## 4. Costos Asociados al Componente de IA (Gemini)

| Modelo             | Uso estimado         | Costo por solicitud | Costo mensual estimado |
|---------------------|------------------------|------------------------|---------------------------|
| `gemini-2.0-flash`  | ~200 análisis/mes      | ~$0.000075 USD          | ~$0.015 USD                |

> El modelo Gemini 2.0 Flash tiene una capa gratuita de **1.500 solicitudes/día**,
> por lo que para el volumen de uso de una municipalidad pequeña el costo
> operacional de IA es **$0 USD/mes** dentro del free tier de Google AI Studio.

## Resumen General

| Categoría                       | Costo estimado (CLP)     |
|------------------------------------|------------------------------|
| Desarrollo (único)                 | $1.260.000                   |
| Infraestructura (año 1)            | $372.300                     |
| Operación y mantención (año 1)     | $1.107.000                   |
| Componente IA (año 1)              | $0 (free tier)                |
| **Total año 1**                    | **$2.739.300**                |
| **Total año 2 en adelante**        | **$1.479.300/año**             |

> Los costos de infraestructura pueden reducirse usando instancias `e2-small`
> (~$13 USD/mes) si el tráfico lo permite, o usando el crédito gratuito de GCP
> ($300 USD para nuevas cuentas).
