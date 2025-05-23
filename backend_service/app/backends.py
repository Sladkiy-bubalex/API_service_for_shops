import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from app.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT аутентификация
    """
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        Проверка JWT токена
        """
        request.user = None

        # Получение заголовка авторизации и префикса.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Некорректный заголовок токена, в заголовке передан один элемент
            return None

        elif len(auth_header) > 2:
            # Некорректный заголовок токена, какие-то лишние пробельные символы
            return None

        # JWT библиотека обычно некорректно обрабатывает
        # тип bytes. Чтобы точно решить это, нам нужно
        # декодировать prefix и token.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        # Мы делегируем фактическую аутентификацию учетных данных методу _authenticate_credentials.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Авторизация пользователя по JWT токену
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except Exception:
            msg = 'Ошибка аутентификации. Неверный токен.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'Данный пользователь деактивирован.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)