from rest_framework import serializers
from .models import Tramite, TipoTramite, DocumentoTramite, HistorialTramite


class TipoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTramite
        fields = ['id', 'nombre', 'descripcion', 'activo', 'requiere_documentos', 'departamento_responsable']


class DocumentoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoTramite
        fields = ['id', 'nombre_original', 'archivo', 'subido_en']


class HistorialTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialTramite
        fields = ['id', 'usuario_nombre', 'usuario_email', 'accion',
                  'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']


class TramiteSerializer(serializers.ModelSerializer):
    documentos = DocumentoTramiteSerializer(many=True, read_only=True)
    historial = HistorialTramiteSerializer(many=True, read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)

    class Meta:
        model = Tramite
        fields = [
            'id', 'codigo_seguimiento', 'tipo', 'tipo_nombre', 'estado', 'descripcion',
            'ciudadano_id', 'ciudadano_email', 'ciudadano_nombre', 'ciudadano_rut',
            'funcionario_id', 'funcionario_nombre', 'funcionario_email',
            'creado_en', 'actualizado_en', 'documentos', 'historial',
        ]
        read_only_fields = ['codigo_seguimiento', 'creado_en', 'actualizado_en']
