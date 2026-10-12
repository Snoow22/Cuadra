# Guía de contribución

Aunque es un proyecto personal, se trabaja como uno de equipo para mostrar el proceso. El detalle vive en `docs/`; esta página sólo resume y enlaza.

## Dónde está cada cosa

| Necesito… | Documento |
|---|---|
| Levantar el proyecto en mi computador | [`docs/inicio-local.md`](docs/inicio-local.md) |
| Saber cómo se nombran ramas y commits, y cómo se publican versiones | [`docs/ramas-y-versionado.md`](docs/ramas-y-versionado.md) |
| Entender qué se construye y con qué reglas | [`docs/requisitos.md`](docs/requisitos.md) |
| Saber por qué se decidió algo | [`docs/decisiones/`](docs/decisiones/) |

## Flujo en cinco pasos

1. Cada historia de usuario (`HU-XX`) es un issue en GitHub.
2. Se trabaja en una rama propia desde `main`: `feature/HU-11-registrar-venta`, `fix/...`, `docs/...`.
3. Los commits siguen Conventional Commits e incluyen el código: `feat(HU-11): registrar venta con varias líneas`.
4. Se abre un Pull Request hacia `main` con la plantilla, y la CI debe pasar.
5. Se fusiona con *Squash and merge* y se borra la rama.

Se avanza por rebanadas verticales: migración, API, tests e interfaz de una funcionalidad antes de pasar a la siguiente.

## Decisiones técnicas

Si un cambio implica una decisión de arquitectura, se registra en `docs/decisiones/` usando `plantilla.md` con el siguiente número correlativo.

## Reglas de oro del proyecto

- Los movimientos nunca se editan ni se eliminan.
- El dinero es siempre entero (CLP), nunca `float`.
- Las reglas importantes se protegen también en la base de datos.
- Ningún secreto entra al repositorio.
