from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer,
    RegistroCiudadanoSerializer,
    CrearFuncionarioSerializer,
)


class LoginView(TokenObtainPairView):
    """Login — retorna access y refresh token con datos del usuario."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_ciudadano(request):
    """Registro público para ciudadanos."""
    serializer = RegistroCiudadanoSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        return Response({
            'mensaje': f'Usuario {usuario.email} registrado correctamente.',
            'usuario': UsuarioSerializer(usuario).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Invalida el refresh token (blacklist)."""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'mensaje': 'Sesión cerrada correctamente.'})
    except Exception:
        return Response({'error': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil(request):
    """Retorna los datos del usuario autenticado."""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_token(request):
    """
    Endpoint que usan los demás servicios para verificar que el token es válido
    y obtener los datos del usuario.
    """
    return Response({
        'valido': True,
        'user_id': request.user.id,
        'email': request.user.email,
        'rol': request.user.rol,
        'departamento': request.user.departamento,
        'rut': request.user.rut,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_staff': request.user.is_staff,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_funcionario(request):
    """Solo admin puede crear funcionarios."""
    if not (request.user.es_admin or request.user.is_staff):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = CrearFuncionarioSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        return Response({
            'mensaje': f'Funcionario {usuario.email} creado correctamente.',
            'usuario': UsuarioSerializer(usuario).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_usuarios(request):
    """Lista de usuarios — solo admin."""
    if not request.user.es_admin:
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)
    usuarios = Usuario.objects.all()
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)
