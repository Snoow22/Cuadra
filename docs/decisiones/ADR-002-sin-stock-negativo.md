# ADR-002: No se permite stock negativo

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

En un negocio pequeño es común vender antes de registrar la compra. Permitir stock negativo evita bloquear la venta, pero un stock negativo casi nunca representa un quiebre real: suele indicar un dato mal registrado. Además, afecta la integridad del historial y del costo promedio.

## Decisión

Una venta que dejaría el stock bajo 0 se rechaza con un 409, indicando el producto y la cantidad disponible. El descuento se hace de forma atómica (`UPDATE ... WHERE stock_actual >= cantidad`) y la base de datos refuerza la regla con `CHECK (stock_actual >= 0)`.

## Alternativas descartadas

- **Permitir negativo con alerta:** más flexible, pero deja datos inconsistentes y debilita el costo promedio.
- **Negativo configurable por negocio:** razonable, pero se pospone a la v2 para mantener acotado el alcance.

## Consecuencias

- Los quiebres se detectan igual (`stock_actual = 0`) y se miden con los movimientos.
- Se pierde la información de demanda no atendida; queda anotada como mejora futura (tabla `demanda_no_atendida`).
- Hay un caso de concurrencia real que resolver y probar (HU-12).
