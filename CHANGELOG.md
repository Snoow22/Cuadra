# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado según [SemVer](https://semver.org/lang/es/) (ver `docs/ramas-y-versionado.md`).

## [Sin publicar]

### Agregado
- Documentación inicial: requisitos, ADR-001 a ADR-007 y guías de ramas, versionado e inicio local.
- API en Django con endpoint `/health` (verifica la base de datos) y sus tests.
- CI con lint, `manage.py check`, verificación de migraciones y tests de la API sobre PostgreSQL.
- HU-01: modelo de usuario propio (`email`, `nombre`, `rol`, `activo`), `POST /auth/login` con sesión de Django y `GET /auth/csrf` (ADR-008).

### Seguridad
- HU-01: el login exige CSRF, responde 401 sin indicar qué campo falló y se bloquea (429) tras 5 fallos en un minuto por cuenta.

### Corregido
- El job `api` de la CI ejecutaba pasos de Node que nunca corrían; ahora instala Python 3.14 y corre `ruff`, `check`, `makemigrations --check` y `pytest`.
