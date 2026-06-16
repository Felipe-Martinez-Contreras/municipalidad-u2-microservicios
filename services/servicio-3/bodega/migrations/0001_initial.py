from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CategoriaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Categoría de producto',
                'verbose_name_plural': 'Categorías de productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='bodega.categoriaproducto')),
                ('unidad_medida', models.CharField(choices=[('unidad', 'Unidad'), ('caja', 'Caja'), ('kg', 'Kilogramo'), ('lt', 'Litro'), ('mt', 'Metro'), ('pack', 'Pack'), ('resma', 'Resma'), ('otro', 'Otro')], default='unidad', max_length=10)),
                ('stock_actual', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('stock_minimo', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('precio_unitario', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('activo', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='MovimientoStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='bodega.producto')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida')], max_length=10)),
                ('cantidad', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('stock_anterior', models.PositiveIntegerField()),
                ('stock_resultante', models.PositiveIntegerField()),
                ('usuario_id', models.IntegerField(null=True)),
                ('usuario_nombre', models.CharField(blank=True, max_length=200)),
                ('usuario_email', models.EmailField(blank=True, max_length=254)),
                ('observacion', models.TextField(blank=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Movimiento de stock',
                'verbose_name_plural': 'Movimientos de stock',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='SolicitudBodega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('departamento_solicitante', models.CharField(max_length=20)),
                ('estado', models.CharField(choices=[('ingresada', 'Ingresada'), ('pendiente', 'Pendiente de aprobación'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('entregada', 'Entregada')], default='ingresada', max_length=20)),
                ('justificacion', models.TextField()),
                ('observacion_respuesta', models.TextField(blank=True)),
                ('solicitante_id', models.IntegerField()),
                ('solicitante_nombre', models.CharField(max_length=200)),
                ('solicitante_email', models.EmailField(max_length=254)),
                ('aprobado_por_id', models.IntegerField(blank=True, null=True)),
                ('aprobado_por_nombre', models.CharField(blank=True, max_length=200)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Solicitud de bodega',
                'verbose_name_plural': 'Solicitudes de bodega',
                'ordering': ['-creado_en'],
                'permissions': [('puede_aprobar_solicitud', 'Puede aprobar o rechazar solicitudes de bodega'), ('puede_entregar_solicitud', 'Puede marcar solicitudes como entregadas')],
            },
        ),
        migrations.CreateModel(
            name='DetalleSolicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='bodega.solicitudbodega')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles_solicitud', to='bodega.producto')),
                ('cantidad_solicitada', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('cantidad_entregada', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'verbose_name': 'Detalle de solicitud',
                'verbose_name_plural': 'Detalles de solicitudes',
            },
        ),
    ]
