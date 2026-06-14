from rest_framework import serializers
from .models import Producto, CategoriaProducto, MovimientoStock, SolicitudBodega, DetalleSolicitud


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    stock_bajo = serializers.BooleanField(read_only=True)
    valor_total_stock = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'unidad_medida', 'stock_actual', 'stock_minimo', 'precio_unitario',
            'activo', 'stock_bajo', 'valor_total_stock', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['creado_en', 'actualizado_en']


class MovimientoStockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'producto', 'producto_nombre', 'tipo', 'cantidad',
            'stock_anterior', 'stock_resultante', 'usuario_nombre',
            'usuario_email', 'observacion', 'fecha',
        ]
        read_only_fields = ['fecha']


class DetalleSolicitudSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleSolicitud
        fields = [
            'id', 'producto', 'producto_nombre',
            'cantidad_solicitada', 'cantidad_entregada',
        ]


class SolicitudBodegaSerializer(serializers.ModelSerializer):
    detalles = DetalleSolicitudSerializer(many=True, read_only=True)

    class Meta:
        model = SolicitudBodega
        fields = [
            'id', 'codigo', 'departamento_solicitante', 'estado', 'justificacion',
            'observacion_respuesta', 'solicitante_id', 'solicitante_nombre',
            'solicitante_email', 'aprobado_por_id', 'aprobado_por_nombre',
            'creado_en', 'actualizado_en', 'detalles',
        ]
        read_only_fields = ['codigo', 'creado_en', 'actualizado_en']
