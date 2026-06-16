from django.db import models


class TipoTramite(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    requiere_documentos = models.BooleanField(default=True)
    departamento_responsable = models.CharField(max_length=20, blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de trámite'
        verbose_name_plural = 'Tipos de trámite'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Tramite(models.Model):
    class EstadoChoices(models.TextChoices):
        INGRESADO = 'ingresado', 'Ingresado'
        EN_REVISION = 'en_revision', 'En revisión'
        OBSERVADO = 'observado', 'Observado'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'
        FINALIZADO = 'finalizado', 'Finalizado'

    codigo_seguimiento = models.CharField(max_length=20, unique=True)
    tipo = models.ForeignKey(TipoTramite, on_delete=models.PROTECT, related_name='tramites')
    estado = models.CharField(max_length=20, choices=EstadoChoices.choices, default=EstadoChoices.INGRESADO)
    descripcion = models.TextField()

    # En vez de FK a Usuario, guardamos solo los datos necesarios del JWT
    ciudadano_id = models.IntegerField()
    ciudadano_email = models.EmailField()
    ciudadano_nombre = models.CharField(max_length=200)
    ciudadano_rut = models.CharField(max_length=12)

    # Funcionario asignado — también solo datos del JWT
    funcionario_id = models.IntegerField(null=True, blank=True)
    funcionario_nombre = models.CharField(max_length=200, blank=True)
    funcionario_email = models.EmailField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trámite'
        verbose_name_plural = 'Trámites'
        ordering = ['-creado_en']
        permissions = [
            ('puede_asignar_tramite', 'Puede asignar trámites a funcionarios'),
            ('puede_cambiar_estado', 'Puede cambiar el estado de los trámites'),
        ]

    def __str__(self):
        return f'{self.codigo_seguimiento} - {self.tipo.nombre} ({self.get_estado_display()})'

    def save(self, *args, **kwargs):
        if not self.codigo_seguimiento:
            ultimo = Tramite.objects.order_by('-id').first()
            numero = (ultimo.id + 1) if ultimo else 1
            from datetime import date
            year = date.today().year
            self.codigo_seguimiento = f'TRM-{year}-{numero:06d}'
        super().save(*args, **kwargs)


class DocumentoTramite(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='tramites/documentos/%Y/%m/')
    nombre_original = models.CharField(max_length=255)
    subido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subido_en']

    def __str__(self):
        return f'{self.nombre_original} ({self.tramite.codigo_seguimiento})'


class HistorialTramite(models.Model):
    class AccionChoices(models.TextChoices):
        CREACION = 'creacion', 'Creación del trámite'
        CAMBIO_ESTADO = 'cambio_estado', 'Cambio de estado'
        ASIGNACION = 'asignacion', 'Asignación a funcionario'
        OBSERVACION = 'observacion', 'Observación agregada'
        DOCUMENTO_ADJUNTO = 'documento_adjunto', 'Documento adjuntado'

    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='historial')

    # Sin FK a Usuario — guardamos datos del JWT
    usuario_id = models.IntegerField(null=True)
    usuario_nombre = models.CharField(max_length=200, blank=True)
    usuario_email = models.EmailField(blank=True)

    accion = models.CharField(max_length=30, choices=AccionChoices.choices)
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tramite.codigo_seguimiento} - {self.get_accion_display()}'
