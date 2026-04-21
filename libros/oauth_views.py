import json
import logging
import urllib.parse
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from urllib.parse import urlencode 
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Configuración de logs y modelo de usuario
logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def google_oauth_callback(request):
    """
    Endpoint que recibe el código de autorización de Google
    y devuelve tokens JWT de nuestra aplicación.
    """
    # 0. Definición dinámica de la URL de redirección
    redirect_uri = getattr(settings, 'OAUTH_REDIRECT_URI', 'http://127.0.0.1:8000/api/auth/google/callback/')

    # 1. Obtener el código de autorización (de POST o GET)
    code = request.data.get('code') or request.query_params.get('code')
    
    if not code:
        error_msg = 'El código de autorización es requerido'
        logger.error(error_msg)
        if request.method == 'GET':
            return redirect(f'/oauth/login/?error={urllib.parse.quote(error_msg)}')
        return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 2. Intercambiar código por access token de Google
        token_url = 'https://oauth2.googleapis.com/token'
        google_config = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']
        
        token_data = {
            'code': code,
            'client_id': google_config['client_id'],
            'client_secret': google_config['secret'],
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        token_response.raise_for_status()
        
        tokens = token_response.json()
        google_access_token = tokens.get('access_token')
        
        if not google_access_token:
            error_msg = 'No se pudo obtener access token de Google'
            logger.error(error_msg)
            return redirect(f'/oauth/login/?error={urllib.parse.quote(error_msg)}')
        
        # 3. Obtener información del usuario de Google
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {google_access_token}'}
        
        userinfo_response = requests.get(userinfo_url, headers=headers, timeout=10)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()
        
        # 4. Crear o actualizar usuario en Django
        email = user_data.get('email')
        if not email:
            error_msg = 'No se pudo obtener el email del usuario'
            return redirect(f'/oauth/login/?error={urllib.parse.quote(error_msg)}')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': user_data.get('given_name', ''),
                'last_name': user_data.get('family_name', ''),
            }
        )
        
        if not created:
            user.first_name = user_data.get('given_name', user.first_name)
            user.last_name = user_data.get('family_name', user.last_name)
            user.save()
        
        # 5. Generar tokens JWT de nuestra aplicación
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # 6. Preparar datos para el frontend
        user_info = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        user_info_json = json.dumps(user_info)
        google_info_json = json.dumps({'picture': user_data.get('picture')})
        
        # Construir URL de redirección final
        final_redirect = (
            f'/oauth/login/?'
            f'access_token={access_token}&'
            f'refresh_token={str(refresh)}&'
            f'user_info={urllib.parse.quote(user_info_json)}&'
            f'google_info={urllib.parse.quote(google_info_json)}&'
            f'message={urllib.parse.quote("Login exitoso")}'
        )
        
        return redirect(final_redirect)
    
    except Exception as e:
        logger.error(f"Error en OAuth: {str(e)}")
        return redirect(f'/oauth/login/?error={urllib.parse.quote(str(e))}')


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_redirect(request):
    """
    Endpoint que redirige al usuario a Google para autorización.
    """
    # Definición dinámica de la URL de redirección
    redirect_uri = getattr(settings, 'OAUTH_REDIRECT_URI', 'http://127.0.0.1:8000/api/auth/google/callback/')
    
    google_config = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']
    scopes = settings.SOCIALACCOUNT_PROVIDERS['google'].get('SCOPE', ['email', 'profile'])
    
    params = {
        'client_id': google_config["client_id"],
        'redirect_uri': redirect_uri,
        'scope': " ".join(scopes),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
    
    return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)