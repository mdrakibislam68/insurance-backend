from seeder.seeders.base_seeder import BaseSeeder
from products.factories.product_factory import ProductFactory
from products.factories.product_schedule_factory import ProductScheduleFactory
from products.factories.product_schedule_date_factory import ProductScheduleDateFactory
import random
class ProductSeeder(BaseSeeder):
	def create_product_schedules_and_dates(self, product):
		schedules = ProductScheduleFactory().create(product, random.randint(1, 5))

		for schedule in schedules:
			ProductScheduleDateFactory().create(schedule, random.randint(1, 5))
	
	def run(self):
		print("Seeding data using ProductFactory...")
		products = ProductFactory().create(10)  # Generate 10 fake records

		for product in products:
			if product.is_bundle:
				bundle_products = ProductFactory().create(random.randint(1, 5), is_bundle=False)

				for bundle_product in bundle_products:
					self.create_product_schedules_and_dates(bundle_product)
					product.bundle_products.add(bundle_product)
			else:
				self.create_product_schedules_and_dates(product)