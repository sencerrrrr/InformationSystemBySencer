from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.conf import settings


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Пропускаем пути аутентификации
        auth_paths = ['/api/auth/login/', '/api/auth/refresh/', '/api/auth/verify/']
        if any(request.path.startswith(path) for path in auth_paths):
            return

        # Извлекаем токен из куки
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if access_token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(access_token)
                request.user = jwt_auth.get_user(validated_token)
                request.auth = validated_token
            except (InvalidToken, AuthenticationFailed):
                # Токен невалиден, пользователь не аутентифицирован
                request.user = None
                request.auth = None