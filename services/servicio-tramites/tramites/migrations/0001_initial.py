from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TipoTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('requiere_documentos', models.BooleanField(default=True)),
                ('departamento_responsable', models.CharField(blank=True, default='', max_length=20)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tipo de trámite',
                'verbose_name_plural': 'Tipos de trámite',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Tramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_seguimiento', models.CharField(max_length=20, unique=True)),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tramites', to='tramites.tipotramite')),
                ('estado', models.CharField(choices=[('ingresado', 'Ingresado'), ('en_revision', 'En revisión'), ('observado', 'Observado'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado'), ('finalizado', 'Finalizado')], default='ingresado', max_length=20)),
                ('descripcion', models.TextField()),
                ('ciudadano_id', models.IntegerField()),
                ('ciudadano_email', models.EmailField(max_length=254)),
                ('ciudadano_nombre', models.CharField(max_length=200)),
                ('ciudadano_rut', models.CharField(max_length=12)),
                ('funcionario_id', models.IntegerField(blank=True, null=True)),
                ('funcionario_nombre', models.CharField(blank=True, max_length=200)),
                ('funcionario_email', models.EmailField(blank=True, max_length=254)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Trámite',
                'verbose_name_plural': 'Trámites',
                'ordering': ['-creado_en'],
                'permissions': [('puede_asignar_tramite', 'Puede asignar trámites a funcionarios'), ('puede_cambiar_estado', 'Puede cambiar el estado de los trámites')],
            },
        ),
        migrations.CreateModel(
            name='DocumentoTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tramite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='tramites.tramite')),
                ('archivo', models.FileField(upload_to='tramites/documentos/%Y/%m/')),
                ('nombre_original', models.CharField(max_length=255)),
                ('subido_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-subido_en'],
            },
        ),
        migrations.CreateModel(
            name='HistorialTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tramite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='tramites.tramite')),
                ('usuario_id', models.IntegerField(null=True)),
                ('usuario_nombre', models.CharField(blank=True, max_length=200)),
                ('usuario_email', models.EmailField(blank=True, max_length=254)),
                ('accion', models.CharField(choices=[('creacion', 'Creación del trámite'), ('cambio_estado', 'Cambio de estado'), ('asignacion', 'Asignación a funcionario'), ('observacion', 'Observación agregada'), ('documento_adjunto', 'Documento adjuntado')], max_length=30)),
                ('estado_anterior', models.CharField(blank=True, max_length=20)),
                ('estado_nuevo', models.CharField(blank=True, max_length=20)),
                ('observacion', models.TextField(blank=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]
