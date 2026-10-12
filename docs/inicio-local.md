# Cuadra — Inicio del proyecto en local

Pasos para levantar la base de datos, la API y el frontend en tu computador. Los comandos funcionan en Windows (PowerShell o Git Bash), macOS y Linux.

> **Estado actual:** hoy sólo existe la base de datos (`docker-compose.yml`). La API y el frontend se crean en la fase 0; los pasos 2 a 6 se vuelven ejecutables cuando termine esa fase. Esta guía se actualiza al cerrarla.

## Requisitos previos

| Herramienta | Versión | Cómo verificar |
|---|---|---|
| Node.js | 20 o superior | `node -v` |
| npm | el que trae Node | `npm -v` |
| Git | cualquiera reciente | `git --version` |
| Docker con Compose | Docker Desktop (en Windows, con WSL 2) o Docker Engine | `docker compose version` |

Docker debe estar **abierto y corriendo** antes del paso 1.

## 0. Clonar y preparar variables de entorno

```bash
git clone https://github.com/Snoow22/Cuadra.git
cd Cuadra
cp .env.example .env
```

En PowerShell, `cp` también funciona (es un alias de `Copy-Item`). Edita `.env` y cambia al menos `POSTGRES_PASSWORD` y `SESSION_SECRET`. Si cambias la contraseña, actualiza también `DATABASE_URL` para que coincida.

Para generar un `SESSION_SECRET` aleatorio:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
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
npm install
npm run migrate        # crea las tablas
npm run dev            # levanta la API en el puerto de API_PORT (por defecto 3000)
```

Probar que responde:

```bash
curl http://localhost:3000/health
```

Debe responder con estado 200. En PowerShell, `curl` es un alias de otro comando: usa `curl.exe` o abre la URL en el navegador.

### Datos de ejemplo

Cuando exista el script de datos de ejemplo (`scripts/`), se ejecutará con:

```bash
npm run seed
```

## 3. Frontend (`web/`)

En otra terminal:

```bash
cd web
npm install
npm run dev
```

Abrir en el navegador: <http://localhost:5173>

El frontend llama a la API en la dirección de `VITE_API_URL` (por defecto `http://localhost:3000`), y la API acepta peticiones del origen definido en `CORS_ORIGIN` (por defecto `http://localhost:5173`). Si cambias un puerto, cambia ambas variables.

## 4. Usuario de prueba

Los usuarios de ejemplo los crea `npm run seed` y se documentan aquí cuando existan (fase 2). Nunca uses una contraseña real en una base local o de demo.

## 5. Todo con Docker Compose

Cuando la API y el frontend tengan su `Dockerfile` (fase 0), se podrá levantar todo con un solo comando:

```bash
docker compose up --build
```

## 6. Pruebas, lint y tipos

Desde `api/`:

```bash
npm run lint
npm run typecheck
npm test
```

Los tests de integración corren contra una base PostgreSQL real y separada de la de desarrollo, para no tocar tus datos. Cómo se crea esa base y qué variable la configura se documenta aquí al terminar la fase 0.

Desde `web/` están disponibles `npm run lint`, `npm run typecheck` y `npm run build`.

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
| `npm install` falla o muestra advertencias de motor | Versión de Node anterior a la 20. Actualiza Node y reintenta. |
| El frontend muestra errores de CORS | `CORS_ORIGIN` no coincide con la dirección donde abriste el frontend. Corrígelo en `.env` y reinicia la API. |
| La API no arranca por falta de una variable | Falta copiar `.env.example` a `.env` o completar un valor. |

## Notas

- `.env` no se sube al repositorio (está en `.gitignore`). La referencia es `.env.example`, que nunca lleva valores reales.
- Antes de abrir un PR, corre lint, tipos y tests en local (ver `docs/ramas-y-versionado.md`, sección 2.3).
