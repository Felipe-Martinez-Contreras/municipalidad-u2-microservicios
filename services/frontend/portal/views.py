import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse


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


# ─── TRÁMITES ──────────────────────────────────────────────────────────────

ESTADOS_TRAMITE = {
    'ingresado': ('Ingresado', 'bg-primary'),
    'en_revision': ('En revisión', 'bg-warning text-dark'),
    'observado': ('Observado', 'bg-danger'),
    'aprobado': ('Aprobado', 'bg-success'),
    'rechazado': ('Rechazado', 'bg-dark'),
    'finalizado': ('Finalizado', 'bg-secondary'),
}


def _headers(request):
    token = request.session.get('access_token')
    return {'Authorization': f'Bearer {token}'}


@login_requerido
def mis_tramites(request):
    usuario = get_usuario(request)
    if usuario.get('rol') != 'ciudadano':
        messages.error(request, 'Esta sección es solo para ciudadanos.')
        return redirect('dashboard')

    try:
        response = requests.get(
            f"{settings.TRAMITES_SERVICE_URL}/tramites/",
            headers=_headers(request),
            timeout=10,
        )
        tramites = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión con el servicio de trámites.')
        tramites = []

    for t in tramites:
        t['estado_display'], t['estado_badge'] = ESTADOS_TRAMITE.get(t['estado'], (t['estado'], 'bg-secondary'))

    return render(request, 'portal/mis_tramites.html', {
        'tramites': tramites,
        'titulo': 'Mis Trámites',
    })


@login_requerido
def crear_tramite(request):
    usuario = get_usuario(request)
    if usuario.get('rol') != 'ciudadano':
        messages.error(request, 'Solo ciudadanos pueden crear trámites.')
        return redirect('dashboard')

    # Obtener tipos de trámite disponibles
    try:
        response = requests.get(
            f"{settings.TRAMITES_SERVICE_URL}/tramites/tipos/",
            headers=_headers(request),
            timeout=10,
        )
        tipos = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        tipos = []

    if request.method == 'POST':
        data = {
            'tipo': request.POST.get('tipo'),
            'descripcion': request.POST.get('descripcion'),
            'ciudadano_id': usuario.get('user_id'),
            'ciudadano_email': usuario.get('email'),
            'ciudadano_nombre': f"{usuario.get('first_name', '')} {usuario.get('last_name', '')}".strip(),
            'ciudadano_rut': usuario.get('rut'),
        }
        try:
            response = requests.post(
                f"{settings.TRAMITES_SERVICE_URL}/tramites/",
                json=data,
                headers=_headers(request),
                timeout=10,
            )
            if response.status_code == 201:
                tramite = response.json()
                messages.success(
                    request,
                    f"Trámite creado exitosamente. Código: {tramite['codigo_seguimiento']}"
                )
                return redirect('mis_tramites')
            else:
                messages.error(request, f"Error al crear trámite: {response.json()}")
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión con el servicio de trámites.')

    return render(request, 'portal/crear_tramite.html', {
        'tipos': tipos,
        'titulo': 'Nuevo Trámite',
    })



@login_requerido
def detalle_tramite(request, codigo):
    usuario = get_usuario(request)
    rol = usuario.get('rol', '')
    puede_cambiar_estado = rol in ['funcionario', 'jefatura', 'admin']

    if request.method == 'POST' and request.POST.get('accion') == 'cambiar_estado':
        data = {
            'estado': request.POST.get('estado'),
            'observacion': request.POST.get('observacion', ''),
        }
        try:
            response = requests.patch(
                f"{settings.TRAMITES_SERVICE_URL}/tramites/{codigo}/",
                json=data,
                headers=_headers(request),
                timeout=10,
            )
            if response.status_code == 200:
                messages.success(request, 'Estado actualizado correctamente.')
            else:
                messages.error(request, f"Error: {response.json()}")
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión.')
        return redirect('detalle_tramite', codigo=codigo)

    try:
        response = requests.get(
            f"{settings.TRAMITES_SERVICE_URL}/tramites/{codigo}/",
            headers=_headers(request),
            timeout=10,
        )
        if response.status_code == 200:
            tramite = response.json()
            tramite['estado_display'], tramite['estado_badge'] = ESTADOS_TRAMITE.get(
                tramite['estado'], (tramite['estado'], 'bg-secondary')
            )
        else:
            messages.error(request, 'Trámite no encontrado.')
            return redirect('mis_tramites')
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión.')
        return redirect('mis_tramites')

    return render(request, 'portal/detalle_tramite.html', {
        'tramite': tramite,
        'usuario': usuario,
        'puede_cambiar_estado': puede_cambiar_estado,
        'titulo': f"Trámite {tramite['codigo_seguimiento']}",
    })

@login_requerido
def bandeja_tramites(request):
    usuario = get_usuario(request)
    if usuario.get('rol') not in ['funcionario', 'jefatura', 'admin']:
        messages.error(request, 'Sin permisos para acceder a esta sección.')
        return redirect('dashboard')

    try:
        response = requests.get(
            f"{settings.TRAMITES_SERVICE_URL}/tramites/bandeja/",
            headers=_headers(request),
            timeout=10,
        )
        data = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión.')
        data = {}

    tramites = data.get('tramites', [])
    for t in tramites:
        t['estado_display'], t['estado_badge'] = ESTADOS_TRAMITE.get(
            t['estado'], (t['estado'], 'bg-secondary')
        )

    return render(request, 'portal/bandeja_tramites.html', {
        'tramites': tramites,
        'totales': data.get('totales', {}),
        'titulo': 'Bandeja de Trámites',
    })


@login_requerido
def inventario(request):
    usuario = get_usuario(request)
    if usuario.get('rol') not in ['bodeguero', 'jefatura', 'admin']:
        messages.error(request, 'Sin permisos para acceder al inventario.')
        return redirect('dashboard')

    try:
        response = requests.get(
            f"{settings.BODEGA_SERVICE_URL}/bodega/inventario/",
            headers=_headers(request),
            timeout=10,
        )
        data = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión.')
        data = {}

    return render(request, 'portal/inventario.html', {
        'productos': data.get('productos', []),
        'total': data.get('total', 0),
        'stock_bajo': data.get('stock_bajo', 0),
        'sin_stock': data.get('sin_stock', 0),
        'titulo': 'Inventario de Bodega',
    })


@login_requerido
def mis_solicitudes(request):
    usuario = get_usuario(request)
    if usuario.get('rol') not in ['funcionario', 'bodeguero', 'jefatura', 'admin']:
        messages.error(request, 'Sin permisos.')
        return redirect('dashboard')

    try:
        response = requests.get(
            f"{settings.BODEGA_SERVICE_URL}/bodega/solicitudes/",
            headers=_headers(request),
            timeout=10,
        )
        solicitudes = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión.')
        solicitudes = []

    return render(request, 'portal/mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'titulo': 'Solicitudes de Bodega',
    })


@login_requerido
def crear_solicitud(request):
    usuario = get_usuario(request)
    if usuario.get('rol') not in ['funcionario', 'bodeguero', 'jefatura', 'admin']:
        messages.error(request, 'Sin permisos.')
        return redirect('dashboard')

    # Obtener productos disponibles
    try:
        response = requests.get(
            f"{settings.BODEGA_SERVICE_URL}/bodega/inventario/",
            headers=_headers(request),
            timeout=10,
        )
        data = response.json() if response.status_code == 200 else {}
        productos = data.get('productos', [])
    except requests.exceptions.ConnectionError:
        productos = []

    if request.method == 'POST':
        data = {
            'justificacion': request.POST.get('justificacion'),
            'departamento_solicitante': usuario.get('departamento', ''),
            'solicitante_id': usuario.get('user_id'),
            'solicitante_nombre': f"{usuario.get('first_name', '')} {usuario.get('last_name', '')}".strip(),
            'solicitante_email': usuario.get('email'),
        }
        try:
            response = requests.post(
                f"{settings.BODEGA_SERVICE_URL}/bodega/solicitudes/",
                json=data,
                headers=_headers(request),
                timeout=10,
            )
            if response.status_code == 201:
                solicitud = response.json()
                solicitud_id = solicitud['id']
                # Agregar productos a la solicitud
                productos_ids = request.POST.getlist('producto_id[]')
                cantidades = request.POST.getlist('cantidad[]')
                for pid, cant in zip(productos_ids, cantidades):
                    if pid and cant:
                        requests.post(
                            f"{settings.BODEGA_SERVICE_URL}/bodega/solicitudes/{solicitud_id}/productos/",
                            json={'producto': int(pid), 'cantidad_solicitada': int(cant)},
                            headers=_headers(request),
                            timeout=10,
                        )
                messages.success(request, f"Solicitud {solicitud['codigo']} creada.")
                return redirect('mis_solicitudes')
            else:
                messages.error(request, f"Error: {response.json()}")
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión.')

    return render(request, 'portal/crear_solicitud.html', {
        'productos': productos,
        'titulo': 'Nueva Solicitud de Bodega',
    })


@login_requerido
def detalle_solicitud(request, solicitud_id):
    usuario = get_usuario(request)
    rol = usuario.get('rol', '')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        data = {'accion': accion}
        if accion in ['aprobada', 'rechazada']:
            data['observacion_respuesta'] = request.POST.get('observacion_respuesta', '')
        try:
            response = requests.patch(
                f"{settings.BODEGA_SERVICE_URL}/bodega/solicitudes/{solicitud_id}/",
                json=data,
                headers=_headers(request),
                timeout=10,
            )
            if response.status_code == 200:
                messages.success(request, f'Solicitud actualizada correctamente.')
            else:
                messages.error(request, f"Error: {response.json()}")
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)

    try:
        response = requests.get(
            f"{settings.BODEGA_SERVICE_URL}/bodega/solicitudes/{solicitud_id}/",
            headers=_headers(request),
            timeout=10,
        )
        if response.status_code == 200:
            solicitud = response.json()
        else:
            messages.error(request, 'Solicitud no encontrada.')
            return redirect('mis_solicitudes')
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Error de conexión.')
        return redirect('mis_solicitudes')

    puede_aprobar = rol in ['jefatura', 'admin'] and solicitud['estado'] in ['ingresada', 'pendiente']
    puede_entregar = rol == 'bodeguero' and solicitud['estado'] == 'aprobada'

    return render(request, 'portal/detalle_solicitud.html', {
        'solicitud': solicitud,
        'puede_aprobar': puede_aprobar,
        'puede_entregar': puede_entregar,
        'titulo': f"Solicitud {solicitud['codigo']}",
    })


@login_requerido
def analisis_ia(request):
    usuario = get_usuario(request)
    if usuario.get('rol') not in ['bodeguero', 'jefatura', 'admin']:
        return JsonResponse({'error': 'Sin permisos.'}, status=403)

    try:
        response = requests.get(
            f"{settings.AI_SERVICE_URL}/ai/analisis-inventario/",
            headers=_headers(request),
            timeout=35,
        )
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': 'Error de conexión con el servicio de IA.'}, status=502)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'El servicio de IA tardó demasiado en responder.'}, status=504)
