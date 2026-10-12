# ADR-005: Nada se borra

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

Los productos están referenciados por compras, ventas y movimientos. Borrarlos rompe el historial. Editar o borrar movimientos haría que el stock deje de poder auditarse.

## Decisión

- Los productos se desactivan (`activo = false`) en lugar de borrarse.
- Los movimientos no se editan ni se eliminan. Un error se corrige con un movimiento inverso.
- Las compras y ventas confirmadas no se editan; se anulan, y la anulación genera movimientos inversos.

## Alternativas descartadas

- **Borrado físico:** simple, pero destruye el historial y rompe claves foráneas.
- **Borrado lógico en todas las tablas:** innecesario para movimientos, que ya son inmutables por diseño.

## Consecuencias

- El historial es completo y auditable.
- Las listas deben filtrar por `activo` para no mostrar productos desactivados.
- Las anulaciones pueden fallar si ya se vendió parte de lo comprado (HU-10), y ese caso se informa con claridad.
