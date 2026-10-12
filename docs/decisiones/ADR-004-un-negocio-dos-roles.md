# ADR-004: Un solo negocio y dos roles

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

Soportar varios negocios (multi-tenant) agrega aislamiento de datos en cada consulta, y permisos finos agregan complejidad que no es el foco de la v1.

## Decisión

La v1 atiende un solo negocio. Hay dos roles: `admin` (todo) y `operador` (registra movimientos, compras y ventas, pero no gestiona usuarios ni anula documentos).

## Alternativas descartadas

- **Multi-negocio desde el inicio:** correcto a largo plazo, pero multiplica el alcance.
- **Un solo rol:** más simple, pero no permite proteger acciones sensibles como anulaciones.

## Consecuencias

- El modelo de datos es más simple y las consultas no necesitan filtrar por negocio.
- Migrar a multi-negocio después exigirá agregar un `negocio_id` a las tablas; queda como mejora futura.
