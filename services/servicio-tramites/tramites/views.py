from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Tramite, TipoTramite, DocumentoTramite, HistorialTramite
from .serializers import (
    TramiteSerializer,
    TipoTramiteSerializer,
    HistorialTramiteSerializer,
    DocumentoTramiteSerializer,
)


def get_user_from_token(request):
    """
    Extrae los datos del usuario desde el JWT.
    Reemplaza el request.user del monolito.
    """
    return {
        'id': request.auth.get('user_id'),
        'email': request.auth.get('email'),
        'nombre': f"{request.auth.get('first_name', '')} {request.auth.get('last_name', '')}".strip(),
        'rol': request.auth.get('rol'),
        'departamento': request.auth.get('departamento'),
        'rut': request.auth.get('rut'),
        'is_staff': request.auth.get('is_staff', False),
    }


def es_ciudadano(user):
    return user['rol'] == 'ciudadano'

def es_funcionario(user):
    return user['rol'] in ['funcionario', 'admin', 'jefatura']

def es_admin(user):
    return user['rol'] == 'admin' or user['is_staff']


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tramites_view(request):
    user = get_user_from_token(request)

    if request.method == 'GET':
        # Ciudadano ve solo sus trámites, funcionario ve todos
        if es_ciudadano(user):
            tramites = Tramite.objects.filter(ciudadano_id=user['id'])
        else:
            tramites = Tramite.objects.all()
        serializer = TramiteSerializer(tramites, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not es_ciudadano(user):
            return Response(
                {'error': 'Solo ciudadanos pueden crear trámites.'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = request.data.copy()
        data['ciudadano_id'] = user['id']
        data['ciudadano_email'] = user['email']
        data['ciudadano_nombre'] = user['nombre']
        data['ciudadano_rut'] = user['rut']

        serializer = TramiteSerializer(data=data)
        if serializer.is_valid():
            tramite = serializer.save()
            HistorialTramite.objects.create(
                tramite=tramite,
                usuario_id=user['id'],
                usuario_nombre=user['nombre'],
                usuario_email=user['email'],
                accion='creacion',
                estado_nuevo='ingresado',
                observacion='Trámite creado por el ciudadano.',
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_tramite(request, codigo):
    user = get_user_from_token(request)
    tramite = get_object_or_404(Tramite, codigo_seguimiento=codigo)

    # Verificar permisos
    if es_ciudadano(user) and tramite.ciudadano_id != user['id']:
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = TramiteSerializer(tramite)
        return Response(serializer.data)

    if request.method == 'PATCH':
        if not es_funcionario(user):
            return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

        estado_anterior = tramite.estado
        serializer = TramiteSerializer(tramite, data=request.data, partial=True)
        if serializer.is_valid():
            tramite_actualizado = serializer.save(
                funcionario_id=user['id'],
                funcionario_nombre=user['nombre'],
                funcionario_email=user['email'],
            )
            HistorialTramite.objects.create(
                tramite=tramite_actualizado,
                usuario_id=user['id'],
                usuario_nombre=user['nombre'],
                usuario_email=user['email'],
                accion='cambio_estado',
                estado_anterior=estado_anterior,
                estado_nuevo=tramite_actualizado.estado,
                observacion=request.data.get('observacion', ''),
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tipos_tramite(request):
    tipos = TipoTramite.objects.filter(activo=True)
    serializer = TipoTramiteSerializer(tipos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_tramite(request, codigo):
    user = get_user_from_token(request)
    tramite = get_object_or_404(Tramite, codigo_seguimiento=codigo)

    if es_ciudadano(user) and tramite.ciudadano_id != user['id']:
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    historial = tramite.historial.all()
    serializer = HistorialTramiteSerializer(historial, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adjuntar_documento(request, codigo):
    user = get_user_from_token(request)
    tramite = get_object_or_404(Tramite, codigo_seguimiento=codigo)

    if tramite.ciudadano_id != user['id']:
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if tramite.estado not in ['ingresado', 'observado']:
        return Response(
            {'error': 'No se pueden adjuntar documentos en este estado.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    archivo = request.FILES.get('archivo')
    if not archivo:
        return Response({'error': 'No se proporcionó archivo.'}, status=status.HTTP_400_BAD_REQUEST)

    documento = DocumentoTramite.objects.create(
        tramite=tramite,
        archivo=archivo,
        nombre_original=archivo.name,
    )

    HistorialTramite.objects.create(
        tramite=tramite,
        usuario_id=user['id'],
        usuario_nombre=user['nombre'],
        usuario_email=user['email'],
        accion='documento_adjunto',
        estado_nuevo=tramite.estado,
        observacion=f'Documento adjuntado: {archivo.name}',
    )

    serializer = DocumentoTramiteSerializer(documento)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bandeja_funcionario(request):
    user = get_user_from_token(request)

    if not es_funcionario(user):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    tramites = Tramite.objects.all().order_by('-creado_en')
    totales = {
        'total': tramites.count(),
        'ingresados': tramites.filter(estado='ingresado').count(),
        'en_revision': tramites.filter(estado='en_revision').count(),
        'observados': tramites.filter(estado='observado').count(),
        'aprobados': tramites.filter(estado='aprobado').count(),
        'rechazados': tramites.filter(estado='rechazado').count(),
        'finalizados': tramites.filter(estado='finalizado').count(),
    }
    serializer = TramiteSerializer(tramites, many=True)
    return Response({'tramites': serializer.data, 'totales': totales})
