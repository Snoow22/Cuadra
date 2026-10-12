# ADR-006: Dinero en enteros

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

Los números de punto flotante no representan con exactitud valores decimales, y los errores de redondeo se acumulan en sumas de dinero. El peso chileno (CLP) no usa decimales en la práctica.

## Decisión

Todos los montos se guardan como enteros en CLP (`BIGINT` o `INTEGER`). Nunca `float`. Si en el futuro se necesitan decimales, se usará `NUMERIC`.

## Alternativas descartadas

- **`FLOAT` / `DOUBLE`:** imprecisos para dinero.
- **`NUMERIC` desde ya:** válido, pero innecesario para CLP y agrega conversiones en JavaScript.

## Consecuencias

- Las sumas y comparaciones son exactas.
- El costo promedio se redondea a entero (ver ADR-003).
- Soportar otra moneda con decimales requerirá un cambio de tipo y una migración.
