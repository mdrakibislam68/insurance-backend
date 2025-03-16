from seeder.factories.base_factory import BaseFactory
from user_management.models import Account

class UserFactory(BaseFactory):
	def create(self, count=1, **overrides):
		objects = []

		for _ in range(count):
			objects.append(Account(
				first_name=self.fake.first_name(),
				last_name=self.fake.last_name(),
				email=self.fake.unique.email(),
				password=self.fake.password(),
			))

		Account.objects.bulk_create(objects)
