from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser


class UsuarioJWT:
    """Usuario virtual construido desde el payload del JWT, sin tocar la BD."""
    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.pk = self.id
        self.email = payload.get('email', '')
        self.username = payload.get('username', '')
        self.rol = payload.get('rol', '')
        self.departamento = payload.get('departamento', '')
        self.rut = payload.get('rut', '')
        self.first_name = payload.get('first_name', '')
        self.last_name = payload.get('last_name', '')
        self.is_staff = payload.get('is_staff', False)
        self.is_active = True
        self.is_authenticated = True

    def __str__(self):
        return self.email


class JWTSinBDAuthentication(JWTAuthentication):
    """Autentica leyendo el JWT sin consultar la base de datos."""

    def get_user(self, validated_token):
        try:
            return UsuarioJWT(validated_token)
        except Exception:
            raise InvalidToken('Token inválido')
