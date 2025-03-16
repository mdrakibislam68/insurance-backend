from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.app_settings import JWTSerializerWithExpiration, TokenSerializer
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from .serializers import ModifiedJWTSerializer


class SocialLoginMain(SocialLoginView):
    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):

            if getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False):
                response_serializer = JWTSerializerWithExpiration
            else:
                response_serializer = ModifiedJWTSerializer

        else:
            response_serializer = TokenSerializer
        return response_serializer


class GoogleLogin(SocialLoginMain):
    authentication_classes = []  # disables authentication
    adapter_class = GoogleOAuth2Adapter
    callback_url = f'{settings.FRONT_END_URL}/login'
    client_class = OAuth2Client


class FacebookLogin(SocialLoginMain):
    authentication_classes = []  # disables authentication
    adapter_class = FacebookOAuth2Adapter
    callback_url = f'{settings.FRONT_END_URL}/login'
    client_class = OAuth2Client
