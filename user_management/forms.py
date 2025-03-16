from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .services.auth_module_services import Account


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name')


class AccountChangeForm(UserChangeForm):
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name')