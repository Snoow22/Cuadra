# Guía de contribución

Aunque es un proyecto personal, se trabaja como uno de equipo para mostrar el proceso.

## Flujo de trabajo

1. Cada historia de usuario (HU-XX) es un issue en GitHub.
2. Se trabaja en una rama propia: `feat/hu-11-registrar-venta`, `fix/...`, `docs/...`.
3. Se abre un pull request hacia `main` y la integración continua debe pasar antes de fusionar.
4. Se avanza por rebanadas verticales: migración, API, tests e interfaz de una funcionalidad antes de pasar a la siguiente.

## Commits

Mensajes pequeños y descriptivos, en formato convencional:

```
feat(ventas): descontar stock de forma atómica
fix(productos): validar SKU duplicado
docs(adr): registrar decisión de costo promedio
test(ventas): cubrir ventas simultáneas
```

## Decisiones técnicas

Si un cambio implica una decisión de arquitectura, se registra en `docs/decisiones/` usando `plantilla.md` con el siguiente número correlativo.

## Reglas de oro del proyecto

- Los movimientos nunca se editan ni se eliminan.
- El dinero es siempre entero (CLP), nunca `float`.
- Las reglas importantes se protegen también en la base de datos.
- Ningún secreto entra al repositorio.
