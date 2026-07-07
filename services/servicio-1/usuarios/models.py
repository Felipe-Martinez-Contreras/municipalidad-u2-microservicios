from django.contrib.auth.models import AbstractUser
from django.db import models
from django_cryptography.fields import encrypt

class Usuario(AbstractUser):
    class RolChoices(models.TextChoices):
        CIUDADANO = 'ciudadano', 'Ciudadano'
        FUNCIONARIO = 'funcionario', 'Funcionario Municipal'
        BODEGUERO = 'bodeguero', 'Encargado de Bodega'
        JEFATURA = 'jefatura', 'Jefatura'
        ADMIN = 'admin', 'Administrador'

    class DeptoChoices(models.TextChoices):
        DIDECO = 'dideco', 'Dideco'
        OMIL = 'omil', 'OMIL'
        TESORERIA = 'tesoreria', 'Tesorería'
        SALUD = 'salud', 'Salud'
        EDUCACION = 'educacion', 'Educación'
        BODEGA = 'bodega', 'Bodega'
        INFORMATICA = 'informatica', 'Informática'
        OTRO = 'otro', 'Otro'

    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    rol = models.CharField(max_length=20, choices=RolChoices.choices, default=RolChoices.CIUDADANO)
    departamento = models.CharField(max_length=20, choices=DeptoChoices.choices, blank=True, default='')
    rut = encrypt(models.CharField(max_length=12))
    telefono = models.CharField(max_length=15, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'rut']

    @property
    def es_ciudadano(self):
        return self.rol == self.RolChoices.CIUDADANO

    @property
    def es_funcionario(self):
        return self.rol == self.RolChoices.FUNCIONARIO

    @property
    def es_bodeguero(self):
        return self.rol == self.RolChoices.BODEGUERO

    @property
    def es_jefatura(self):
        return self.rol == self.RolChoices.JEFATURA

    @property
    def es_admin(self):
        return self.rol == self.RolChoices.ADMIN or self.is_superuser

    class Meta:
        db_table = 'usuarios_usuario'
