from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Correo electrónico')),
                ('rol', models.CharField(choices=[('ciudadano', 'Ciudadano'), ('funcionario', 'Funcionario Municipal'), ('bodeguero', 'Encargado de Bodega'), ('jefatura', 'Jefatura'), ('admin', 'Administrador')], default='ciudadano', max_length=20)),
                ('departamento', models.CharField(blank=True, choices=[('dideco', 'Dideco'), ('omil', 'OMIL'), ('tesoreria', 'Tesorería'), ('salud', 'Salud'), ('educacion', 'Educación'), ('bodega', 'Bodega'), ('informatica', 'Informática'), ('otro', 'Otro')], default='', max_length=20)),
                ('rut', models.CharField(max_length=12, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=15)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'usuarios_usuario',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
