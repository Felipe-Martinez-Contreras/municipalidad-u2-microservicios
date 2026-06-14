import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect


def get_usuario(request):
    return request.session.get('usuario')

def login_requerido(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('access_token'):
            messages.error(request, 'Debes iniciar sesión.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def inicio(request):
    if request.session.get('access_token'):
        return redirect('dashboard')
    return render(request, 'portal/inicio.html')


def login_view(request):
    if request.session.get('access_token'):
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            response = requests.post(
                f"{settings.AUTH_SERVICE_URL}/api/auth/login/",
                json={'email': email, 'password': password},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                request.session['access_token'] = data['access']
                request.session['refresh_token'] = data['refresh']

                # Decodificar payload del JWT sin verificar (ya fue verificado por auth)
                import base64, json
                payload = data['access'].split('.')[1]
                payload += '=' * (4 - len(payload) % 4)
                usuario = json.loads(base64.b64decode(payload))
                request.session['usuario'] = usuario

                messages.success(request, f"¡Bienvenido/a, {usuario.get('first_name') or usuario.get('username')}!")
                return redirect('dashboard')
            else:
                messages.error(request, 'Credenciales inválidas.')
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión con el servidor de autenticación.')

    return render(request, 'portal/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')


def registro_view(request):
    if request.session.get('access_token'):
        return redirect('dashboard')

    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'username': request.POST.get('username'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'rut': request.POST.get('rut'),
        }
        try:
            response = requests.post(
                f"{settings.AUTH_SERVICE_URL}/api/auth/registro/",
                json=data,
                timeout=10,
            )
            if response.status_code == 201:
                messages.success(request, '¡Registro exitoso! Inicia sesión.')
                return redirect('login')
            else:
                messages.error(request, f"Error en el registro: {response.json()}")
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión.')

    return render(request, 'portal/registro.html')


@login_requerido
def dashboard_view(request):
    usuario = get_usuario(request)
    rol = usuario.get('rol', '')

    contexto = {
        'rol_display': {
            'ciudadano': 'Ciudadano',
            'funcionario': 'Funcionario Municipal',
            'bodeguero': 'Encargado de Bodega',
            'jefatura': 'Jefatura',
            'admin': 'Administrador',
        }.get(rol, rol),
        'depto_display': usuario.get('departamento') or 'No asignado',
    }
    return render(request, 'portal/dashboard.html', contexto)
