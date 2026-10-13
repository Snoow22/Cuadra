# ADR-007 — Backend en Django

**Estado:** Aceptada

## Contexto

El plan inicial era una API en Node.js con TypeScript, `pg` y migraciones SQL a mano. Para este proyecto importan la integridad de los datos (RN de stock, restricciones, transacciones) y escribir poco código propio. Además, el autor ya conoce Django.

## Decisión

- **Django + PostgreSQL**, con el ORM de Django y sus migraciones.
- `psycopg` 3 como driver, `django-environ` para la configuración (`DATABASE_URL`), `pytest-django` para los tests y `ruff` como linter.
- **Django REST Framework** se agrega junto con el primer endpoint real (HU-01), no antes.
- `INSTALLED_APPS` queda vacío en la fase 0. El modelo de usuario propio (`AUTH_USER_MODEL`) se define en la fase 2, **antes de la primera migración**.
- El descuento de stock sigue siendo atómico ([ADR-002](ADR-002-sin-stock-negativo.md)):

  ```python
  with transaction.atomic():
      filas = Producto.objects.filter(pk=pk, stock_actual__gte=cantidad).update(
          stock_actual=F("stock_actual") - cantidad
      )
      if filas == 0:
          raise StockInsuficiente
  ```
- Las reglas de integridad (cantidad > 0, stock >= 0, etc.) se declaran en `Meta.constraints` de los modelos, para que las garantice la base y no sólo el código.

## Alternativas descartadas

- **Node + Express + `pg` + `node-pg-migrate`:** más control, pero hay que armar a mano validación, autenticación y migraciones.
- **Node + Prisma o Drizzle:** ORM con tipos, pero con menos soporte para restricciones y actualizaciones atómicas con condición.

## Consecuencias

- Dos lenguajes en el repo (Python en `api/`, TypeScript en `web/`).
- La documentación OpenAPI se genera en la fase 7 con la herramienta de DRF que se elija entonces.
- Se requiere Python 3.12 o superior (Django 6.1); el desarrollo y la CI usan 3.14.
