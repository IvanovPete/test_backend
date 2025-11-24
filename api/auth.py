from .models import User
import logging

logger = logging.getLogger('api')


def get_user_from_token(request):
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
        else:
            token = auth_header
    
    if not token and hasattr(request, 'body'):
        try:
            import json
            body = json.loads(request.body)
            token = body.get('token')
        except:
            pass
    
    if not token:
        logger.warning('Токен не найден в запросе')
        return None
    
    try:
        user = User.objects.get(token=token)
        return user
    except User.DoesNotExist:
        logger.warning(f'Пользователь с токеном не найден')
        return None

