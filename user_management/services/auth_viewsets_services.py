import time

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken

from user_management.models import EmailUpdateRequest, PasswordReset
from user_management.tasks import send_account_activate_email, send_account_reset_password_email, \
    send_email_update_link, send_customer_account_reset_password_email
from user_management.utils.token_generator import account_active_token_generator, reset_password_token_generator
from .auth_module_services import Account


def send_signup_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = account_active_token_generator.make_token(user)
    context = {
        'url': f'{settings.FRONT_END_URL}/auth/verify-account?uuid={uidb64}&token={token}'
    }
    send_account_activate_email.delay(user.email, context)


def send_update_email_link(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = account_active_token_generator.make_token(user)
    context = {
        'recipient_name': user.first_name,
        'url': f'{settings.FRONT_END_URL}/dashboard/update-email?uuid={uidb64}&token={token}'
    }
    send_email_update_link.delay(user.email, context)


def verify_user(uuid):
    user_id = force_str(urlsafe_base64_decode(uuid))
    user = Account.objects.get(pk=user_id)
    user.is_active = True
    user.save()

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'Your account has been successfully activated!',
        'user': {
            'id': user.id,
            'first_name': str(user.first_name),
            'last_name': str(user.last_name),
            'email': str(user.email),
            'role': str(user.groups.first()),
            'is_staff': str(user.is_staff),
            'is_superuser': str(user.is_superuser),
            'permissions': [] if user.is_superuser else user.get_all_permissions(),
        }
    }


def update_email(uuid):
    user_id = force_str(urlsafe_base64_decode(uuid))
    user = Account.objects.get(pk=user_id)
    update_request = EmailUpdateRequest.objects.get(user_id=user_id)
    user.email = update_request.new_email
    user.save()


def login_user(email):
    user = Account.objects.get(email__iexact=email)
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'first_name': str(user.first_name),
            'last_name': str(user.last_name),
            'email': str(user.email),
            'role': str(user.groups.first()),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'permissions': [] if user.is_superuser else user.get_all_permissions(),
        }
    }


def login_customer(email):
    user = Account.objects.get(email__iexact=email)
    refresh = RefreshToken.for_user(user)

    return {
        'id': user.id,
        'customer_id': user.customer.id,
        'avatar': str(user.avatar),
        'first_name': str(user.first_name),
        'last_name': str(user.last_name),
        'email': str(user.email),
        'phone': str(user.phone),
        'note': str(user.customer.note),
        'booking_info_checked': user.customer.booking_info_checked,
        'booking_conditions_checked': user.customer.booking_conditions_checked,
        'receive_booking_updates_checked': user.customer.receive_booking_updates_checked,
        'custom_fields': user.customer.custom_fields,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'wallet_balance': str(user.customer.wallet_balance),
        'reward_points': str(user.customer.reward_points),
        'referral_code': str(user.customer.referral_code),
    }


def send_reset_password_email(email):
    user = Account.objects.get(email__iexact=email)
    uidb64 = urlsafe_base64_encode(force_bytes(f"{user.id}-{int(time.time())}"))
    token = reset_password_token_generator.make_token(user)
    context = {
        'url': f'{settings.FRONT_END_URL}/auth/reset-password?uuid={uidb64}&token={token}'
    }
    send_account_reset_password_email.delay(user.email, context)


def send_reset_password_secretkey(email):
    user = Account.objects.get(email__iexact=email)
    uidb64 = urlsafe_base64_encode(force_bytes(f"{user.id}-{int(time.time())}"))
    token = reset_password_token_generator.make_token(user)
    PasswordReset.objects.create(email=user.email, token=token, secretkey=uidb64)
    context = {
        'recipient_name': user.first_name,
        'secretkey': uidb64
    }
    send_customer_account_reset_password_email.delay(user.email, context)


def reset_password(**validated_data):
    decoded_value = force_str(urlsafe_base64_decode(validated_data['uuid']))
    id, _ = decoded_value.split('-')
    user = Account.objects.get(pk=id)
    user.password = make_password(validated_data['password2'])
    user.save()


def reset_customer_password(**validated_data):
    decoded_value = force_str(urlsafe_base64_decode(validated_data['uuid']))
    id, _ = decoded_value.split('-')
    user = Account.objects.get(pk=id)
    user.password = make_password(validated_data['password2'])
    user.save()


def change_password(user, password):
    user.set_password(password)
    user.save()
