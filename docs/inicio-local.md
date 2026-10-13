# Cuadra — Inicio del proyecto en local

Pasos para levantar la base de datos, la API y el frontend en tu computador. Los comandos funcionan en Windows (PowerShell o Git Bash), macOS y Linux.

> **Estado actual:** existen la base de datos (`docker-compose.yml`) y la API con el endpoint `/health`. El frontend y los `Dockerfile` llegan en la fase 0; los pasos 3 y 5 se vuelven ejecutables entonces.

## Requisitos previos

| Herramienta | Versión | Cómo verificar |
|---|---|---|
| Python | 3.12 o superior | `python --version` |
| Node.js (sólo frontend) | 20 o superior | `node -v` |
| Git | cualquiera reciente | `git --version` |
| Docker con Compose | Docker Desktop (en Windows, con WSL 2) o Docker Engine | `docker compose version` |

Docker debe estar **abierto y corriendo** antes del paso 1.

## 0. Clonar y preparar variables de entorno

```bash
git clone https://github.com/Snoow22/Cuadra.git
cd Cuadra
cp .env.example .env
```

En PowerShell, `cp` también funciona (es un alias de `Copy-Item`). Edita `.env` y cambia al menos `POSTGRES_PASSWORD` y `DJANGO_SECRET_KEY`. Si cambias la contraseña, actualiza también `DATABASE_URL` para que coincida.

Para generar una `DJANGO_SECRET_KEY` aleatoria:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 1. Base de datos (PostgreSQL en Docker)

```bash
docker compose up -d db
```

Verificar que esté sana (la columna *STATUS* debe decir `healthy`):

```bash
docker compose ps
```

Entrar a la base para revisar las tablas (con los valores por defecto de `.env.example`; si cambiaste usuario o base, usa los tuyos):

```bash
docker compose exec db psql -U inventario -d inventario -c "\dt"
```

Antes de aplicar las migraciones (paso 2) la lista estará vacía. Es lo esperado.

## 2. API (`api/`)

```bash
cd api
python -m venv .venv
```

Activa el entorno virtual (hay que hacerlo en cada terminal nueva):

| Terminal | Comando |
|---|---|
| PowerShell | `.venv\Scripts\Activate.ps1` |
| Git Bash | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

Luego:

```bash
pip install -r requirements-dev.txt
python manage.py migrate         # crea las tablas
python manage.py runserver       # levanta la API en http://localhost:8000
```

Probar que responde:

```bash
curl http://localhost:8000/health
```

Debe responder 200 con `{"status": "ok", "db": "up", ...}`. En PowerShell, `curl` es un alias de otro comando: usa `curl.exe` o abre la URL en el navegador.

### Datos de ejemplo

Cuando exista el script de datos de ejemplo (`scripts/`), se documentará aquí cómo ejecutarlo.

## 3. Frontend (`web/`)

En otra terminal:

```bash
cd web
npm install
npm run dev
```

Abrir en el navegador: <http://localhost:5173>

El frontend llama a la API en la dirección de `VITE_API_URL` (por defecto `http://localhost:8000`). Cuando el frontend empiece a llamar a la API se agregará CORS y se usará `CORS_ORIGIN` (por defecto `http://localhost:5173`). Si cambias un puerto, cambia ambas variables.

## 4. Usuario de prueba

Los usuarios de ejemplo los creará el script de datos de ejemplo y se documentan aquí cuando existan (fase 2). Nunca uses una contraseña real en una base local o de demo.

## 5. Todo con Docker Compose

Cuando la API y el frontend tengan su `Dockerfile` (fase 0), se podrá levantar todo con un solo comando:

```bash
docker compose up --build
```

## 6. Pruebas y lint

Desde `api/` (con el entorno virtual activado):

```bash
ruff check .
python manage.py check
pytest
```

`pytest` crea y borra por sí solo una base separada (`test_inventario`), así que no toca tus datos de desarrollo.

Desde `web/` estarán disponibles `npm run lint`, `npm run typecheck` y `npm run build` cuando exista el frontend.

## Comandos útiles

| Quiero… | Comando |
|---|---|
| Detener la base de datos | `docker compose down` |
| Ver los logs de la base | `docker compose logs -f db` |
| Borrar la base y empezar de cero | `docker compose down -v` (**elimina todos los datos locales**) |
| Ver los contenedores activos | `docker compose ps` |

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `Cannot connect to the Docker daemon` o similar | Docker no está abierto. Inicia Docker Desktop y espera a que diga que está corriendo. |
| `port is already allocated` (5432) | Otro PostgreSQL usa ese puerto. Cambia `POSTGRES_PORT` en `.env` y el puerto dentro de `DATABASE_URL`. |
| `password authentication failed` tras cambiar la contraseña en `.env` | PostgreSQL guarda las credenciales al crear el volumen por primera vez. Ejecuta `docker compose down -v` y vuelve a levantar la base (borra los datos locales). |
| `Activate.ps1 cannot be loaded` (PowerShell) | La política de ejecución bloquea scripts. Ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, o usa Git Bash. |
| `ImproperlyConfigured: Set the DJANGO_SECRET_KEY environment variable` | Falta copiar `.env.example` a `.env` o completar `DJANGO_SECRET_KEY`. El `.env` debe estar en la raíz del repo, no en `api/`. |
| `connection refused` al migrar o en `/health` | La base no está arriba o el puerto de `DATABASE_URL` no coincide con `POSTGRES_PORT`. Revisa `docker compose ps`. |
| `No matching distribution found` al instalar | Versión de Python no soportada (menor a 3.12). Actualiza Python y recrea el entorno virtual. |
| `pip` o `python` no son los del proyecto | El entorno virtual no está activado. Actívalo (paso 2). |
| El frontend muestra errores de CORS | Aún no se configura CORS en la API; se agrega cuando el frontend empiece a consumirla. |

## Notas

- `.env` no se sube al repositorio (está en `.gitignore`). La referencia es `.env.example`, que nunca lleva valores reales.
- Antes de abrir un PR, corre lint y tests en local (ver `docs/ramas-y-versionado.md`, sección 2.3).
