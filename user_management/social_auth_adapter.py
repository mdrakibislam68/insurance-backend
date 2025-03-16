from django.db.models import Q
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .services.auth_module_services import Account


class SocialAuthAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        try:
            if sociallogin.user.email:
                user = Account.objects.get(email__iexact=sociallogin.user.email)
                if user:
                    if SocialAccount.objects.filter(Q(user_id=user.id) & Q(provider='google') | Q(provider='facebook')).count() == 0:
                        sociallogin.connect(request, user)

        # Create a response object
        except Account.DoesNotExist:
            pass