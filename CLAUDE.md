# Cuadra — instrucciones para Claude Code

Inventario para pequeños negocios. API en Django + PostgreSQL (`api/`), frontend en React + Vite (`web/`).

## Antes de implementar
- Lee la historia de usuario en `docs/requisitos.md` (reglas RN-XX y criterios de aceptación) y los ADR en `docs/decisiones/`.
- Flujo de ramas, commits, PR y migraciones: `docs/ramas-y-versionado.md` (reglas para agentes en la sección 9).
- Arranque local: `docs/inicio-local.md`.

## Reglas que no se rompen
- Los movimientos son la fuente de verdad; `stock_actual` se actualiza en la misma transacción (ADR-001).
- Nunca stock negativo; el descuento es atómico: `filter(pk=..., stock_actual__gte=n).update(stock_actual=F(...) - n)` dentro de `transaction.atomic()`, y 0 filas actualizadas = stock insuficiente (ADR-002).
- Nada se borra: se desactiva o se anula con movimientos inversos (ADR-005).
- Dinero en enteros CLP, nunca `float` (ADR-006).
- Las reglas de integridad van en `Meta.constraints` de los modelos.
- Cada RN afectada lleva su test de integración contra PostgreSQL real.

## Cómo trabajar
- Una historia de usuario por rama y por PR: `feature/HU-XX-descripcion`. Nunca commitear en `main`.
- Commits convencionales con código: `feat(HU-11): ...`; migraciones con tipo `db`.
- Antes de dar algo por listo, desde `api/` con el venv activado: `ruff check .`, `python manage.py check`, `python manage.py makemigrations --check --dry-run` y `pytest`.
- Cambios en modelos: migración nombrada (`makemigrations -n HU_XX_...`), probada aplicar y deshacer.
- Actualiza `CHANGELOG.md` (sección `[Sin publicar]`) y los docs/ADR si el cambio lo requiere.
- Sin dependencias nuevas sin justificarlo. Sin secretos ni `.env` en el diff.
