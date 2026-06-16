def usuario_context(request):
    """Inyecta el usuario JWT en todas las templates."""
    return {
        'user': request.session.get('usuario', None),
    }
