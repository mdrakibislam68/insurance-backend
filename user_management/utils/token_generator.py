from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class AccountActiveTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


account_active_token_generator = AccountActiveTokenGenerator()


class ResetPasswordTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return text_type(user.password) + text_type(user.pk) + text_type(timestamp)


reset_password_token_generator = ResetPasswordTokenGenerator()


