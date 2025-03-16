from seeder.factories.base_factory import BaseFactory
from products.models import Product

class ProductFactory(BaseFactory):
	def create(self, count=1, **overrides):
		objects = []

		for _ in range(count):
			data = {
                "status": self.fake.random_element(Product.STATUS_CHOICES)[0],
                "visibility": self.fake.random_element(Product.VISIBILITY_CHOICES)[0],
                "is_bundle": self.fake.boolean(),
                "is_virtual": self.fake.boolean(),
                "is_downloadable": False,
                "title": self.fake.sentence(),
                "slug": self.fake.slug(),
                "description": self.fake.paragraph(),
                "regular_price": self.fake.random_number(digits=5),
                "sale_price": self.fake.random_number(digits=5),
            }
			data.update(overrides)

			try:
				objects.append(Product(**data))
			except Exception as e:
				print('Error creating product factory:', e)
		
		return Product.objects.bulk_create(objects)
