from seeder.seeders.base_seeder import BaseSeeder
from user_management.factories.user_factory import UserFactory

class UserSeeder(BaseSeeder):
	def run(self):
		print("Seeding data using UserFactory...")
		UserFactory().create(10)  # Generate 10 fake records
