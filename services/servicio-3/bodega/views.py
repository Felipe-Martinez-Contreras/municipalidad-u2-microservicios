from django.db import models as django_models
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Producto, CategoriaProducto, MovimientoStock, SolicitudBodega, DetalleSolicitud
from .serializers import (
    ProductoSerializer,
    CategoriaProductoSerializer,
    MovimientoStockSerializer,
    SolicitudBodegaSerializer,
    DetalleSolicitudSerializer,
)


def get_user_from_token(request):
    """Extrae datos del usuario desde el JWT."""
    return {
        'id': request.auth.get('user_id'),
        'email': request.auth.get('email'),
        'nombre': f"{request.auth.get('first_name', '')} {request.auth.get('last_name', '')}".strip(),
        'rol': request.auth.get('rol'),
        'departamento': request.auth.get('departamento', ''),
        'is_staff': request.auth.get('is_staff', False),
    }


def es_bodeguero(user):
    return user['rol'] in ['bodeguero', 'admin']

def es_jefatura(user):
    return user['rol'] in ['jefatura', 'admin']

def es_funcionario(user):
    return user['rol'] in ['funcionario', 'bodeguero', 'jefatura', 'admin']

def es_admin(user):
    return user['rol'] == 'admin' or user['is_staff']


# ─── INVENTARIO ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventario(request):
    user = get_user_from_token(request)
    if not (es_bodeguero(user) or es_jefatura(user) or es_funcionario(user)):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    productos = Producto.objects.filter(activo=True).select_related('categoria')
    
    # Filtros opcionales
    categoria = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')
    stock_bajo = request.GET.get('stock_bajo')

    if categoria:
        productos = productos.filter(categoria_id=categoria)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda) | \
                    productos.filter(codigo__icontains=busqueda)
    if stock_bajo:
        productos = productos.filter(stock_actual__lte=django_models.F('stock_minimo'))

    serializer = ProductoSerializer(productos, many=True)
    return Response({
        'productos': serializer.data,
        'total': productos.count(),
        'stock_bajo': sum(1 for p in productos if p.stock_bajo),
        'sin_stock': productos.filter(stock_actual=0).count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_producto(request, producto_id):
    user = get_user_from_token(request)
    if not (es_bodeguero(user) or es_jefatura(user)):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    producto = get_object_or_404(Producto, pk=producto_id)
    movimientos = producto.movimientos.all()[:50]
    return Response({
        'producto': ProductoSerializer(producto).data,
        'movimientos': MovimientoStockSerializer(movimientos, many=True).data,
    })


# ─── SOLICITUDES ──────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def solicitudes(request):
    user = get_user_from_token(request)

    if not es_funcionario(user):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if es_bodeguero(user) or es_jefatura(user):
            solicitudes_qs = SolicitudBodega.objects.all()
        else:
            solicitudes_qs = SolicitudBodega.objects.filter(solicitante_id=user['id'])
        serializer = SolicitudBodegaSerializer(solicitudes_qs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        data = request.data.copy()
        data['solicitante_id'] = user['id']
        data['solicitante_nombre'] = user['nombre']
        data['solicitante_email'] = user['email']
        if not data.get('departamento_solicitante'):
            data['departamento_solicitante'] = user['departamento']

        serializer = SolicitudBodegaSerializer(data=data)
        if serializer.is_valid():
            solicitud = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_solicitud(request, solicitud_id):
    user = get_user_from_token(request)
    solicitud = get_object_or_404(SolicitudBodega, pk=solicitud_id)

    # Permisos: creador, bodeguero, jefatura, admin
    if not (
        solicitud.solicitante_id == user['id']
        or es_bodeguero(user)
        or es_jefatura(user)
    ):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = SolicitudBodegaSerializer(solicitud)
        return Response(serializer.data)

    if request.method == 'PATCH':
        accion = request.data.get('accion')

        # Aprobar o rechazar — solo jefatura/admin
        if accion in ['aprobada', 'rechazada']:
            if not es_jefatura(user):
                return Response({'error': 'Sin permisos para aprobar.'}, status=status.HTTP_403_FORBIDDEN)
            solicitud.estado = accion
            solicitud.aprobado_por_id = user['id']
            solicitud.aprobado_por_nombre = user['nombre']
            solicitud.observacion_respuesta = request.data.get('observacion_respuesta', '')
            solicitud.save()
            return Response(SolicitudBodegaSerializer(solicitud).data)

        # Entregar — solo bodeguero
        if accion == 'entregada':
            if not es_bodeguero(user):
                return Response({'error': 'Sin permisos para entregar.'}, status=status.HTTP_403_FORBIDDEN)
            if solicitud.estado != 'aprobada':
                return Response({'error': 'La solicitud debe estar aprobada.'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                solicitud.estado = 'entregada'
                solicitud.save()

                for detalle in solicitud.detalles.all():
                    producto = detalle.producto
                    cantidad = min(detalle.cantidad_solicitada, producto.stock_actual)
                    if cantidad > 0:
                        stock_anterior = producto.stock_actual
                        producto.stock_actual -= cantidad
                        producto.save()

                        MovimientoStock.objects.create(
                            producto=producto,
                            tipo='salida',
                            cantidad=cantidad,
                            stock_anterior=stock_anterior,
                            stock_resultante=producto.stock_actual,
                            usuario_id=user['id'],
                            usuario_nombre=user['nombre'],
                            usuario_email=user['email'],
                            observacion=f'Entrega por solicitud {solicitud.codigo}',
                        )
                        detalle.cantidad_entregada = cantidad
                        detalle.save()

            return Response(SolicitudBodegaSerializer(solicitud).data)

        return Response({'error': 'Acción no válida.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_producto_solicitud(request, solicitud_id):
    user = get_user_from_token(request)
    solicitud = get_object_or_404(SolicitudBodega, pk=solicitud_id)

    if solicitud.solicitante_id != user['id'] and not es_admin(user):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if solicitud.estado not in ['ingresada', 'pendiente']:
        return Response({'error': 'No se puede modificar esta solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = DetalleSolicitudSerializer(data=request.data)
    if serializer.is_valid():
        detalle = serializer.save(solicitud=solicitud)
        return Response(DetalleSolicitudSerializer(detalle).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categorias(request):
    cats = CategoriaProducto.objects.filter(activo=True)
    serializer = CategoriaProductoSerializer(cats, many=True)
    return Response(serializer.data)
