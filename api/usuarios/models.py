from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.functions import Now


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra):
        usuario = self.model(email=self.normalize_email(email), nombre=nombre, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, password=None, **extra):
        return self.create_user(email, nombre, password, rol=Usuario.Rol.ADMIN, **extra)


class Usuario(AbstractBaseUser):
    class Rol(models.TextChoices):
        ADMIN = "admin"
        OPERADOR = "operador"

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150)
    rol = models.CharField(max_length=10, choices=Rol, default=Rol.OPERADOR)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(db_default=Now())

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        db_table = "usuarios"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rol__in=["admin", "operador"]), name="usuarios_rol_valido"
            ),
        ]

    # Django (ModelBackend, login) lee is_active; aquí el campo se llama `activo` (ADR-005).
    @property
    def is_active(self):
        return self.activo


class IntentoLoginFallido(models.Model):
    """Registro técnico efímero para el bloqueo de login (ADR-008); no es dato de negocio."""

    email = models.CharField(max_length=254)
    creado_en = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = "intentos_login_fallidos"
        indexes = [models.Index(fields=["email", "creado_en"])]
