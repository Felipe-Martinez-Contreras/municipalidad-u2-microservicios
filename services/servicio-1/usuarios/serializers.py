from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['email'] = user.email
        token['username'] = user.username
        token['rol'] = user.rol
        token['departamento'] = user.departamento
        token['rut'] = user.rut
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        return token


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'rol', 'departamento', 'rut', 'telefono', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegistroCiudadanoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['email', 'username', 'first_name', 'last_name', 'rut', 'telefono', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.rol = Usuario.RolChoices.CIUDADANO
        usuario.set_password(password)
        usuario.save()
        return usuario


class CrearFuncionarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['email', 'username', 'first_name', 'last_name',
                  'rut', 'telefono', 'rol', 'departamento', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario
