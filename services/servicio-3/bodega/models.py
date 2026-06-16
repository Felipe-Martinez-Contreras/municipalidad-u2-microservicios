from django.db import models
from django.core.validators import MinValueValidator


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría de producto'
        verbose_name_plural = 'Categorías de productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class UnidadChoices(models.TextChoices):
        UNIDAD = 'unidad', 'Unidad'
        CAJA = 'caja', 'Caja'
        KILO = 'kg', 'Kilogramo'
        LITRO = 'lt', 'Litro'
        METRO = 'mt', 'Metro'
        PACK = 'pack', 'Pack'
        RESMA = 'resma', 'Resma'
        OTRO = 'otro', 'Otro'

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, related_name='productos')
    unidad_medida = models.CharField(max_length=10, choices=UnidadChoices.choices, default=UnidadChoices.UNIDAD)
    stock_actual = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def valor_total_stock(self):
        return self.stock_actual * self.precio_unitario


class MovimientoStock(models.Model):
    class TipoChoices(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SALIDA = 'salida', 'Salida'

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TipoChoices.choices)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock_anterior = models.PositiveIntegerField()
    stock_resultante = models.PositiveIntegerField()

    # Sin FK a Usuario — datos del JWT
    usuario_id = models.IntegerField(null=True)
    usuario_nombre = models.CharField(max_length=200, blank=True)
    usuario_email = models.EmailField(blank=True)

    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de stock'
        verbose_name_plural = 'Movimientos de stock'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})'


class SolicitudBodega(models.Model):
    class EstadoChoices(models.TextChoices):
        INGRESADA = 'ingresada', 'Ingresada'
        PENDIENTE = 'pendiente', 'Pendiente de aprobación'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        ENTREGADA = 'entregada', 'Entregada'

    codigo = models.CharField(max_length=20, unique=True)
    departamento_solicitante = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, choices=EstadoChoices.choices, default=EstadoChoices.INGRESADA)
    justificacion = models.TextField()
    observacion_respuesta = models.TextField(blank=True)

    # Sin FK a Usuario — datos del JWT
    solicitante_id = models.IntegerField()
    solicitante_nombre = models.CharField(max_length=200)
    solicitante_email = models.EmailField()

    aprobado_por_id = models.IntegerField(null=True, blank=True)
    aprobado_por_nombre = models.CharField(max_length=200, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de bodega'
        verbose_name_plural = 'Solicitudes de bodega'
        ordering = ['-creado_en']
        permissions = [
            ('puede_aprobar_solicitud', 'Puede aprobar o rechazar solicitudes de bodega'),
            ('puede_entregar_solicitud', 'Puede marcar solicitudes como entregadas'),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.get_estado_display()}'

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = SolicitudBodega.objects.order_by('-id').first()
            numero = (ultimo.id + 1) if ultimo else 1
            from datetime import date
            year = date.today().year
            self.codigo = f'SOL-{year}-{numero:06d}'
        super().save(*args, **kwargs)


class DetalleSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudBodega, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_solicitud')
    cantidad_solicitada = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cantidad_entregada = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Detalle de solicitud'
        verbose_name_plural = 'Detalles de solicitudes'

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad_solicitada}'
