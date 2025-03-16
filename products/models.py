from django.db import models
from common_bases.base_models import BaseModel, HasSlugModel


class Product(BaseModel, HasSlugModel):
	STATUS_CHOICES = [
		('draft', 'Draft'),
		('published', 'Published'),
		('archived', 'Archived'),
	]

	VISIBILITY_CHOICES = [
		('public', 'Public'),
		('private', 'Private'),
	]

	status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='draft')
	visibility = models.CharField(max_length=255, choices=VISIBILITY_CHOICES, default='public')
	is_bundle = models.BooleanField(default=False)
	is_virtual = models.BooleanField(default=False)
	is_downloadable = models.BooleanField(default=False)
	title = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)
	featured_image = models.ImageField(upload_to='products/featured_images', null=True, blank=True)
	regular_price = models.DecimalField(max_digits=10, decimal_places=2)
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	categories = models.ManyToManyField('ProductCategory', related_name='products')
	tags = models.ManyToManyField('ProductTag', related_name='products')
	bundle_products = models.ManyToManyField('self', related_name='bundle_products')


class ProductCategory(BaseModel):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True)
	description = models.TextField(null=True, blank=True)
	featured_image = models.ImageField(upload_to='products/categories/featured_images', null=True, blank=True)


class ProductTag(BaseModel):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True)


class ProductMedia(BaseModel):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
	media_file = models.FileField(upload_to='products/media', null=True, blank=True)
	download_limit = models.IntegerField(null=True, blank=True)
	download_expiry = models.IntegerField(null=True, blank=True)


class ProductSchedule(BaseModel):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='schedules')
	name = models.CharField(max_length=255, null=True, blank=True)
	description = models.TextField(null=True, blank=True)


class ProductScheduleDate(BaseModel):
	schedule = models.ForeignKey(ProductSchedule, on_delete=models.CASCADE, related_name='dates')
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	is_zoom_meeting = models.BooleanField(default=False)
	zoom_meeting_id = models.CharField(max_length=255, null=True, blank=True)