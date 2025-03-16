from seeder.factories.base_factory import BaseFactory
from products.models import ProductSchedule

class ProductScheduleFactory(BaseFactory):
	def create(self, product, count=1, **overrides):
		objects = []

		for _ in range(count):
			objects.append(ProductSchedule(
				product=product,
				name=self.fake.sentence(),
			))

		return ProductSchedule.objects.bulk_create(objects)
