# ADR-003: Costo promedio ponderado

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

El problema que motiva el proyecto es relacionar el costo de compra con el precio de venta sin cruzar planillas a mano. Hay que elegir un método para valorar el inventario y calcular el margen.

## Decisión

Se usa costo promedio ponderado. Al registrar una compra:

`costo_promedio = (stock × costo_promedio + cantidad × costo_nuevo) / (stock + cantidad)`, redondeado a entero.

Cada línea de venta guarda `precio_unitario` y `costo_unitario` vigente en ese momento, como "foto" para calcular el margen.

## Alternativas descartadas

- **PEPS / FIFO (por lotes):** más exacto, pero exige llevar lotes y complica anulaciones y consultas.
- **Último costo de compra:** simple, pero distorsiona el margen cuando los precios varían.

## Consecuencias

- El margen por venta (HU-13) se calcula sin cruces manuales.
- El margen histórico no cambia aunque cambie el costo después, porque se guardó la foto.
- El redondeo a entero introduce diferencias mínimas que se aceptan y se documentan.
