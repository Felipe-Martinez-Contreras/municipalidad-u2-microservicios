import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def es_bodeguero_o_similar(user):
    return user.rol in ['bodeguero', 'jefatura', 'admin']


def construir_prompt(productos):
    lineas = []
    for p in productos:
        lineas.append(
            f"- {p['nombre']} (código {p['codigo']}, categoría {p.get('categoria_nombre', 'N/A')}): "
            f"stock actual {p['stock_actual']} {p['unidad_medida']}, "
            f"stock mínimo {p['stock_minimo']}, "
            f"precio unitario ${p['precio_unitario']}"
        )
    inventario_texto = "\n".join(lineas) if lineas else "No hay productos registrados."

    prompt = (
        "Eres un asistente de gestión de bodega para una municipalidad chilena. "
        "A continuación se entrega el inventario actual de productos. "
        "Analiza el inventario y entrega recomendaciones breves y concretas en español, "
        "en un máximo de 5 puntos, enfocándote en: productos con stock bajo o en cero que "
        "deberían reponerse con prioridad, productos con exceso de stock, y cualquier "
        "observación relevante para la gestión eficiente de la bodega. "
        "Responde en formato de lista, sin introducciones largas.\n\n"
        f"Inventario:\n{inventario_texto}"
    )
    return prompt


def llamar_gemini(prompt):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    texto = data['candidates'][0]['content']['parts'][0]['text']
    return texto


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analisis_inventario(request):
    user = request.user

    if not es_bodeguero_o_similar(user):
        return Response({'error': 'Sin permisos.'}, status=status.HTTP_403_FORBIDDEN)

    if not settings.GEMINI_API_KEY:
        return Response(
            {'error': 'GEMINI_API_KEY no configurada en el servidor.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Obtener inventario desde servicio-bodega, propagando el JWT del usuario
    headers = {'Authorization': request.headers.get('Authorization', '')}
    try:
        resp = requests.get(
            f"{settings.BODEGA_SERVICE_URL}/bodega/inventario/",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        productos = data.get('productos', [])
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'No se pudo obtener el inventario: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    prompt = construir_prompt(productos)

    try:
        analisis = llamar_gemini(prompt)
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'Error al consultar el servicio de IA: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except (KeyError, IndexError):
        return Response(
            {'error': 'Respuesta inesperada del servicio de IA.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({
        'total_productos': len(productos),
        'analisis': analisis,
    })
