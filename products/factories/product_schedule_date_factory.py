from seeder.factories.base_factory import BaseFactory
from products.models import ProductScheduleDate

class ProductScheduleDateFactory(BaseFactory):
	def create(self, schedule, count=1, **overrides):
		objects = []

		for _ in range(count):
			data = {
				"schedule": schedule,
				"date": self.fake.date_between(start_date='-30d', end_date='+30d'),
				"start_time": self.fake.time(),
				"end_time": self.fake.time(),
			}
			data.update(overrides)

			try:
				objects.append(ProductScheduleDate(**data))
			except Exception as e:
				print('Error creating product schedule date factory:', e)

		return ProductScheduleDate.objects.bulk_create(objects)
