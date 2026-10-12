# Cuadra — Guía de ramas y versionado

> **Aplica a:** todo el repositorio (`api/`, `web/`, migraciones y documentación) y a cualquier agente que trabaje en él (Claude Code).
> **Principio base:** `main` siempre está estable y desplegable. Nada entra a `main` sin Pull Request y sin CI en verde.
> **Origen:** adaptada de la guía de Limpiecito ERP. Se conservan sus convenciones (nombres de ramas, Conventional Commits, SemVer, CHANGELOG y plantilla de PR). Lo que cambia es el modelo de ramas, que aquí es más simple (ver sección 1).

---

## 1. Modelo de ramas

```
main ───●─────────●──────────●──────────●──────▶  DEMO
        │ v0.1.0  │ v0.2.0   │ v0.2.1   │ v0.3.0
        ▲         ▲          ▲
        │         │          └── fix/venta-descuenta-stock-doble
        │         └───────────── feature/HU-03-crear-producto
        └─────────────────────── chore/fase-0-esqueleto
```

| Rama | Propósito | Nace de | Se integra en | Duración |
|---|---|---|---|---|
| `main` | Código estable. Cada versión publicada es un tag sobre esta rama. | — | — | Permanente |
| `feature/<código>-<desc>` | Una historia de usuario (HU) | `main` | `main` | 1–4 días |
| `refactor/<código>-<desc>` | Un requerimiento no funcional (RNF) o deuda técnica | `main` | `main` | 1–4 días |
| `fix/<desc>` | Corrección de un error | `main` | `main` | Horas |
| `test/<desc>` | Sólo tests | `main` | `main` | Horas |
| `docs/<desc>` | Sólo documentación | `main` | `main` | Horas |
| `chore/<desc>` | Configuración, dependencias, CI, scripts | `main` | `main` | Horas |

### ¿Por qué no hay `develop`?

En Limpiecito existe porque hay un ambiente de pruebas separado, un dueño que aprueba en cada Sprint Review y usuarios reales en producción. Cuadra no tiene nada de eso: es un proyecto de portafolio que se despliega desde el primer día. Una rama `develop` sólo agregaría pasos sin proteger a nadie.

Si algún día aparecen usuarios reales o un ambiente de pruebas separado, se agrega `develop` siguiendo el modelo de la guía de Limpiecito.

### Convención de nombres

- Minúsculas, palabras separadas por guion, sin tildes ni ñ.
- El código del backlog va en mayúsculas y siempre se incluye cuando exista (`HU-XX` de `docs/requisitos.md`, `RNF-XX` para requisitos no funcionales).

```
feature/HU-03-crear-producto
feature/HU-11-registrar-venta
test/HU-12-ventas-simultaneas
refactor/RNF-05-restricciones-en-db
fix/venta-descuenta-stock-doble
docs/guia-ramas
chore/fase-0-esqueleto
```

### Historias grandes

Si una historia tomará más de 4 días, se divide en ramas incrementales que dejan el sistema funcionando en cada merge:

```
feature/HU-11a-endpoint-registrar-venta     (API y reglas de negocio)
feature/HU-11b-descuento-atomico            (transacción y test de concurrencia)
feature/HU-11c-pantalla-de-venta            (interfaz en React)
```

---

## 2. Flujo de trabajo diario

### 2.1 Empezar una historia

```bash
git switch main
git pull origin main
git switch -c feature/HU-03-crear-producto
```

### 2.2 Durante el desarrollo

```bash
git add -p                                   # revisar qué se agrega
git commit -m "feat(HU-03): endpoint POST /productos"
git push -u origin feature/HU-03-crear-producto
```

Al menos **una vez al día** se trae lo nuevo de `main`, para que los conflictos aparezcan chicos:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease                  # nunca --force a secas
```

> `rebase` y `--force-with-lease` sólo se usan en **ramas propias**. Nunca sobre `main`.

### 2.3 Terminar una historia

1. Rebase final sobre `origin/main` y verificación local: lint, tipos, tests y build (ver `docs/inicio-local.md`).
2. Abrir un Pull Request **hacia `main`** con la plantilla de la sección 8.3.
3. Esperar la CI en verde.
4. **Revisión:**
   - Si trabajas solo, revisa tu propio diff en la pestaña *Files changed* como si fuera de otra persona: busca secretos, logs de depuración, migraciones sin reversa y reglas de negocio sin test.
   - Si hay otro integrante, él revisa y aprueba. Nadie aprueba su propio PR.
5. Hacer merge con **Squash and merge**: la historia queda como un solo commit en `main`, con el título del PR (formato de la sección 3).
6. La rama se borra automáticamente (opción de la sección 8.2).
7. Cerrar el issue de la historia. El PR puede incluir `Closes #N` en la descripción.

---

## 3. Mensajes de commit (Conventional Commits)

```
<tipo>(<código o alcance>): <descripción en imperativo, minúscula, sin punto final>
```

El título del PR sigue el mismo formato, porque es el que queda en `main` tras el squash.

| Tipo | Uso | Ejemplo |
|---|---|---|
| `feat` | Funcionalidad nueva | `feat(HU-11): registrar venta con varias líneas` |
| `fix` | Corrección de error | `fix(HU-12): evitar stock negativo en ventas simultáneas` |
| `refactor` | Cambio interno sin alterar comportamiento | `refactor(RNF-01): validación de entrada con Zod` |
| `perf` | Mejora de rendimiento | `perf(RNF-04): índice en movimientos por producto y fecha` |
| `test` | Tests | `test(HU-12): diez ventas en paralelo sobre stock 5` |
| `docs` | Documentación | `docs: guía de ramas y versionado` |
| `chore` | Configuración, dependencias, CI, scripts | `chore: agregar docker-compose con PostgreSQL` |
| `db` | Sólo migraciones o datos de ejemplo | `db(HU-09): tablas de compras y compra_items` |

Si un cambio rompe el contrato de la API que consume `web/` (o de un consumidor externo, si algún día existe), se agrega al pie del mensaje:

```
BREAKING CHANGE: GET /productos devuelve { data, meta } en lugar de un arreglo
```

---

## 4. Versionado (Semantic Versioning)

Formato **`vMAYOR.MENOR.PARCHE`**.

| Parte | Cuándo sube | Ejemplo |
|---|---|---|
| **MAYOR** | Cambio incompatible en el contrato de la API | `v1.4.0` → `v2.0.0` |
| **MENOR** | Se completa una fase con funcionalidades nuevas | `v0.2.0` → `v0.3.0` |
| **PARCHE** | Corrección que afecta a la demo pública | `v0.4.0` → `v0.4.1` |

Mientras el proyecto está en `0.x`, la API puede cambiar entre versiones menores. `v1.0.0` es la primera versión completa (la v1 de `docs/requisitos.md`).

### Plan de versiones

| Versión | Fase | Contenido |
|---|---|---|
| `v0.1.0` | 0 | Esqueleto andante: API con `/health`, web, CI y despliegue con URL pública |
| `v0.2.0` | 1 y 2 | Modelo de datos y migraciones; autenticación, roles y primer producto (HU-01, 02, 03) |
| `v0.3.0` | 3 | Gestión de productos y ajustes (HU-04 a 07) |
| `v0.4.0` | 4 | Compras y ventas, con el test de concurrencia (HU-09, 11, 12) |
| `v0.5.0` | 5 | Consultas: historial, margen, panel de stock y quiebres (HU-08, 13 a 16) |
| `v0.6.0` | 6 | Anulaciones (HU-10, 14) |
| `v1.0.0` | 7 | Pulido: errores uniformes, documentación OpenAPI, README y demo |

Si una fase no queda terminada, **no se crea versión**: su contenido sale en la versión siguiente. Los números no se saltan.

No se usan versiones candidatas (`-rc.N`), porque no hay un ambiente de pruebas separado donde mostrarlas.

### Dónde vive el número de versión

- `package.json` de `api/` y de `web/` (`"version": "0.2.0"`), ambos con el mismo número.
- Tag anotado de Git sobre `main`.
- `CHANGELOG.md` en la raíz.
- Opcional: que `/health` incluya la versión desplegada, útil para confirmar qué hay en la demo.

---

## 5. Publicar una versión

### 5.1 Checklist antes de publicar

- [ ] Todos los PR de la fase están integrados en `main`.
- [ ] La CI de `main` está en verde.
- [ ] Las migraciones se probaron (aplicar y deshacer) sobre una copia de la base de la demo.
- [ ] Los criterios de aceptación de las historias de la fase están verificados.
- [ ] `CHANGELOG.md` tiene el contenido en la sección `[Sin publicar]`.
- [ ] La demo funciona de punta a punta.

### 5.2 Pasos

La rama principal está protegida, así que el cambio de versión también entra por PR.

```bash
git switch main
git pull
git switch -c chore/release-v0.2.0

# Subir la versión en ambos package.json, sin crear tag todavía
cd api
npm version 0.2.0 --no-git-tag-version
cd ../web
npm version 0.2.0 --no-git-tag-version
cd ..

# Mover [Sin publicar] del CHANGELOG a [0.2.0] - AAAA-MM-DD
git commit -am "chore(release): v0.2.0"
git push -u origin chore/release-v0.2.0
```

Luego, en GitHub: PR hacia `main`, CI en verde y *Squash and merge*. Después, el tag sobre `main`:

```bash
git switch main
git pull
git tag -a v0.2.0 -m "Fase 2: acceso y primer producto"
git push origin v0.2.0
```

### 5.3 Despliegue

El mecanismo concreto (despliegue automático desde `main` o manual) se decide en la fase 0 y se anota aquí.

1. Si la versión incluye migraciones destructivas o que transforman datos, respaldo previo de la base (`pg_dump` o snapshot del proveedor).
2. Ejecutar las migraciones pendientes.
3. Verificación rápida: `/health`, inicio de sesión y una venta de ejemplo.
4. Crear el **GitHub Release** desde el tag, pegando la sección del CHANGELOG.

### 5.4 Rollback

Con *Squash and merge* no hay commit de merge, así que se revierte el commit de la versión. Como `main` está protegida, la reversión también entra por PR.

```bash
git switch main
git pull
git switch -c fix/revertir-v0.2.0
git revert <sha-del-commit-de-la-version>
git push -u origin fix/revertir-v0.2.0
```

Alternativa rápida: redesplegar el tag anterior mientras se prepara la reversión.

Después, deshacer las migraciones de esa versión en orden inverso. Si una migración ya transformó datos, se restaura el respaldo del paso 5.3.1.

---

## 6. Corrección de errores

No hay rama `hotfix`: un error es un `fix/` que sigue el mismo flujo que cualquier cambio.

1. `fix/<desc>` desde `main`, con un test que reproduzca el error.
2. PR hacia `main`, CI en verde, *Squash and merge*.
3. Si el error afecta a la demo pública, se publica una versión **PARCHE** (por ejemplo `v0.4.1`) y se registra en el CHANGELOG bajo `[0.4.1]`. Si no la afecta, la corrección sale en la siguiente versión menor.

---

## 7. Migraciones de base de datos

Es el principal foco de conflicto entre ramas. La herramienta de migraciones se elige en la fase 1; los nombres exactos de los scripts se documentan aquí cuando exista.

1. **Una migración por cambio lógico**, siempre reversible.
2. Nombre con marca de tiempo y el código de la historia, por ejemplo `..._HU-03_crear-tabla-productos`.
3. **Antes del merge**, rebase sobre `main` y verificación del ciclo completo en una base local desechable: deshacer todo y volver a aplicar.
4. Nunca editar una migración que ya está en `main`; si hay que corregir, se crea una migración nueva.
5. El esquema sólo cambia mediante migraciones. Prohibido modificar tablas a mano en la demo o sincronizar el esquema automáticamente con un ORM.
6. Las restricciones que protegen las reglas de negocio (`CHECK`, `UNIQUE`, claves foráneas) viven en migraciones (RNF-05).
7. Si dos ramas necesitan tocar la misma tabla, se secuencian: una espera el merge de la otra.

---

## 8. Configuración de GitHub

### 8.1 Protección de `main` (Settings → Rules o Branches)

| Regla | `main` |
|---|---|
| Requerir Pull Request antes del merge | ✅ |
| Aprobaciones requeridas | 0 si trabajas solo (GitHub no deja aprobar el propio PR) · 1 si hay otro integrante |
| Descartar aprobaciones al subir nuevos commits | ✅ |
| Requerir que pasen los checks `API (lint, tipos, tests, build)` y `Web (lint, tipos, build)` | ✅ |
| Requerir rama actualizada antes del merge | ✅ |
| Prohibir force push | ✅ |
| Prohibir eliminación | ✅ |

Los dos checks aparecen en la lista de GitHub sólo después de que la CI corrió al menos una vez; por eso esta regla se configura tras el primer PR (sección 11).

### 8.2 Opciones del repositorio (Settings → General)

- Permitir **sólo Squash merging**. Desactivar *Merge commits* y *Rebase merging*.
- Activar **Automatically delete head branches**.

### 8.3 Plantilla de Pull Request

Se guarda como `.github/pull_request_template.md`:

```markdown
## Historia de usuario
Código: HU-XX — <nombre>
Fase: N

## Qué cambia
- 

## Cómo probar
1. 

## Criterios de aceptación
- [ ] 
- [ ] 

## Migraciones
- [ ] No incluye migraciones
- [ ] Incluye migraciones (probadas aplicar y deshacer en local)

## Checklist
- [ ] Rebase sobre main actualizado
- [ ] Lint, tipos y tests pasan en local
- [ ] Sin secretos ni `.env` en el diff
- [ ] Las reglas de negocio afectadas (RN-XX) tienen test
- [ ] Documentación o ADR actualizado, si corresponde
```

### 8.4 Archivos que nunca se versionan

Ver `.gitignore` del repositorio: `.env`, `node_modules/`, `dist/`, `coverage/`, logs y datos locales de Docker.

Cuidado con copiar de Limpiecito la regla `*.sql`: allí se ignora porque los volcados no se suben, pero en Cuadra las migraciones pueden ser archivos SQL. Si necesitas ignorar volcados, usa `*.dump` o una carpeta `backups/`.

---

## 9. Reglas para Claude Code y otros agentes

Pueden copiarse tal cual a un `CLAUDE.md` en la raíz del repositorio.

1. Trabaja siempre en una rama `feature/<código>-<desc>`, `refactor/<código>-<desc>` o `fix/<desc>` creada desde `main` actualizado.
2. **Nunca** hagas commit ni push directo a `main`, ni crees tags.
3. Una historia por rama; commits en formato Conventional Commits, incluyendo el código.
4. Antes de terminar: rebase sobre `origin/main`, lint, tipos y tests pasando, y migraciones verificadas (aplicar y deshacer).
5. Termina abriendo el Pull Request con la plantilla; la revisión y el merge los hace la persona.
6. No uses `git push --force`; si es necesario, sólo `--force-with-lease` y sólo en tu propia rama.
7. Respeta `docs/requisitos.md` y los ADR de `docs/decisiones/`. Si una tarea contradice una decisión registrada, avisa en vez de cambiarla.

---

## 10. CHANGELOG.md

Formato basado en *Keep a Changelog*. Cada entrada lleva el código de la historia:

```markdown
## [Sin publicar]
### Agregado
### Cambiado
### Corregido
### Seguridad

## [0.2.0] - AAAA-MM-DD
### Agregado
- HU-01: inicio de sesión con límite de intentos.
- HU-03: crear producto con SKU único.
```

El ejemplo de `[0.2.0]` es sólo ilustrativo; la fecha real se escribe al publicar.

---

## 11. Puesta en marcha (una sola vez)

1. El primer commit del proyecto va directo a `main` (requisitos y estructura inicial). Es la única vez.
2. Crear la rama `docs/guia-ramas` con esta guía, `docs/inicio-local.md`, `CHANGELOG.md`, `CONTRIBUTING.md` y la plantilla de PR actualizada:
   ```bash
   git switch -c docs/guia-ramas
   git add .
   git commit -m "docs: guía de ramas, inicio local y changelog"
   git push -u origin docs/guia-ramas
   ```
3. Abrir el PR hacia `main`. Es el primer PR del proyecto y hace correr la CI por primera vez. Hacer *Squash and merge*.
4. Con la CI ya ejecutada, configurar la protección de `main` y las opciones de merge (secciones 8.1 y 8.2).
5. No se crea ningún tag todavía: la primera versión es `v0.1.0`, al cerrar la fase 0.

---

## 12. Referencia rápida

| Quiero… | Comando / acción |
|---|---|
| Empezar una historia | `git switch main`, `git pull`, `git switch -c feature/HU-XX-desc` |
| Traer cambios de main | `git fetch` y `git rebase origin/main` |
| Subir tras un rebase | `git push --force-with-lease` |
| Ver en qué rama estoy y qué cambió | `git status` · `git log --oneline --graph -15` |
| Guardar trabajo a medias | `git stash` / `git stash pop` |
| Deshacer el último commit (sin perder cambios) | `git reset --soft HEAD~1` |
| Ver qué versión está publicada | `git describe --tags origin/main` |
| Listar versiones | `git tag -l "v*" --sort=-v:refname` |
| Resolver un conflicto de rebase | editar archivos → `git add <archivo>` → `git rebase --continue` (o `--abort`) |
| Corregir un error | Sección 6 |
