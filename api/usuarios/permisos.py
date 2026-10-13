"""Permisos por rol (HU-02, ADR-004). Las vistas protegidas los reutilizan tal cual."""

from rest_framework.permissions import BasePermission

from .models import Usuario


class EsOperadorOAdmin(BasePermission):
    """Movimientos, compras y ventas: cualquier usuario con sesión y rol válido."""

    message = "No tienes permiso para realizar esta acción."

    def has_permission(self, request, view):
        usuario = request.user
        return usuario.is_authenticated and usuario.rol in (Usuario.Rol.ADMIN, Usuario.Rol.OPERADOR)


class EsAdmin(BasePermission):
    """Gestión de usuarios y anulaciones de documentos."""

    message = "Esta acción es solo para administradores."

    def has_permission(self, request, view):
        usuario = request.user
        return usuario.is_authenticated and usuario.rol == Usuario.Rol.ADMIN
