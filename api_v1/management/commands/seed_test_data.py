# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Group
# from agents.models import Agent
# from bookings.models import Booking
# from customers.models import Customer
# from locations.models import Location
# from payment_system.models import PaymentSetting, Currency
# from rooms.models import Room
# from services.models import Service
# from django.utils import timezone
# from datetime import datetime
#
# from user_management.models import Account
#
#
# class Command(BaseCommand):
#     help = 'Seed the database with initial data.'
#
#     def handle(self, *args, **kwargs):
#         self.current_time = datetime(2025, 2, 8, 6, 3, 5, tzinfo=timezone.utc)
#         self.setup_groups()
#         self.setup_payloads()
#
#     def setup_groups(self):
#         self.practitioner_group, created = Group.objects.get_or_create(name='Practitioner')
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created Practitioner group'))
#
#     def setup_payloads(self):
#         # Create test user account
#         # Account = get_user_model()
#         user_account, created = Account.objects.get_or_create(
#             email='akibislam68@example.com',
#             defaults={
#                 'first_name': 'Rakib',
#                 'last_name': 'Islam',
#                 'date_joined': self.current_time,
#                 'is_active': True,
#                 'is_staff': True,
#                 'is_superuser': True
#             }
#         )
#         if created:
#             user_account.set_password('strong_password123')
#             user_account.save()
#             self.stdout.write(self.style.SUCCESS('Successfully created user account'))
#         else:
#             self.stdout.write(self.style.SUCCESS('User account already exists'))
#
#         # Create test agent
#         agent, created = Agent.objects.get_or_create(
#             account=user_account,
#             defaults={
#                 'display_name': "Rakib Islam",
#                 'status': "active",
#                 'additional_email': "additional@example.com",
#                 'additional_phone': "+1234567890",
#                 'title': "Senior Booking Agent",
#                 'bio': "Experienced booking agent with expertise in service management",
#                 'highlight_label_1': "Experience",
#                 'highlight_value_1': "5+ years",
#                 'highlight_label_2': "Speciality",
#                 'highlight_value_2': "VIP Bookings",
#                 'highlight_label_3': "Languages",
#                 'highlight_value_3': "English, Spanish",
#                 'is_custom_schedule': True
#             }
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created agent'))
#
#         # Create test customer
#         customer, created = Customer.objects.get_or_create(
#             account=user_account,
#             defaults={
#                 'note': "Test customer note",
#                 'admin_note': "Test admin note",
#                 'booking_info_checked': True,
#                 'booking_conditions_checked': True,
#                 'receive_booking_updates_checked': True,
#                 'custom_fields': {
#                     "phone": "+1234567890",
#                     "address": "Test Address"
#                 }
#             }
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created customer'))
#
#         # Create test service
#         service, created = Service.objects.get_or_create(
#             name="Test Service",
#             defaults={
#                 'buffer_before': 0,
#                 'buffer_after': 15,
#                 'duration_minutes': 30,
#                 'timeblock_interval': 45,
#                 'capacity_min': 1,
#                 'capacity_max': 4,
#             }
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created service'))
#
#         # Create test currency
#         currency, created = Currency.objects.get_or_create(
#             code='USD',
#             defaults={'name': 'US Dollar'}
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created currency'))
#
#         # Create test payment settings
#         payment_settings, created = PaymentSetting.objects.get_or_create(
#             application_id='sandbox-sq0idb-VJJ8KguPiAg5v6Re65mfLw',
#             defaults={
#                 'access_token': 'EAAAl4bd-HYtUUduV0088-X_uodvogy-nM3-ffZmva4f_rJy1oW00uS1HGKR_wz-',
#                 'location_id': 'LR9D9VK6M24TH',
#                 'country': 'US',
#                 'currency_code': currency,
#                 'environment': 'sandbox',
#                 'allow_paying_locally': False,
#                 'webhook_url': 'https://your-test-webhook.com/webhook',
#                 'webhook_secret': 'whsec_test_secret'
#             }
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created payment settings'))
#
#         # Create test location
#         location, created = Location.objects.get_or_create(
#             name="Test Location",
#             display_name="Test Location Display Name",
#             location="123 Test Street",
#             location_email="testlocation@example.com",
#             location_phone="1234567890",
#             status="active"
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created location'))
#
#         # Create test room
#         room, created = Room.objects.get_or_create(
#             name="Room Without Image",
#             defaults={'location': location}
#         )
#         if created:
#             self.stdout.write(self.style.SUCCESS('Successfully created room'))
#
#         # Create additional test users for signup/login testing
#         test_users = [
#             {
#                 'email': 'test1@example.com',
#                 'password': 'test1password123',
#                 'first_name': 'Test1',
#                 'last_name': 'User1'
#             },
#             {
#                 'email': 'test2@example.com',
#                 'password': 'test2password123',
#                 'first_name': 'Test2',
#                 'last_name': 'User2'
#             }
#         ]
#
#         for user_data in test_users:
#             user, created = Account.objects.get_or_create(
#                 email=user_data['email'],
#                 defaults={
#                     'first_name': user_data['first_name'],
#                     'last_name': user_data['last_name'],
#                     'date_joined': self.current_time,
#                     'is_active': True
#                 }
#             )
#             if created:
#                 user.set_password(user_data['password'])
#                 user.save()
#                 self.stdout.write(
#                     self.style.SUCCESS(f'Successfully created test user: {user_data["email"]}')
#                 )
#
#         self.stdout.write(self.style.SUCCESS('Seeding completed successfully'))