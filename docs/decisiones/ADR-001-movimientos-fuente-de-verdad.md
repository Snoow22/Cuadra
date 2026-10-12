# ADR-001: Los movimientos son la fuente de verdad del stock

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

El stock de un producto puede guardarse como un número que se modifica, o calcularse a partir de todo lo que pasó con él. Si solo se guarda el número, no hay forma de saber cómo se llegó a él ni de detectar errores. Si solo se calcula, cada consulta de existencias recorre todo el historial.

## Decisión

Cada cambio de stock se registra como un movimiento inmutable (`entrada`, `salida`, `ajuste_positivo`, `ajuste_negativo`). Además, `productos.stock_actual` se guarda como valor en caché y se actualiza en la misma transacción que crea el movimiento.

## Alternativas descartadas

- **Solo un campo `stock` editable:** rápido, pero sin trazabilidad ni forma de auditar o reconstruir el pasado.
- **Solo calcular desde movimientos:** trazable, pero lento al crecer el historial y sin posibilidad de una restricción `CHECK` simple sobre el stock.

## Consecuencias

- El historial siempre cuadra con el stock, porque ambos cambian en la misma transacción.
- Se puede reconstruir el stock en cualquier fecha, lo que habilita el indicador de quiebres (HU-16).
- Hay dos representaciones del mismo dato; se necesita un test que verifique que `stock_actual` coincide con la suma de movimientos.
