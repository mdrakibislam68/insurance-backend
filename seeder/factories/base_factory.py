from abc import ABC, abstractmethod
from faker import Faker

class BaseFactory(ABC):
	"""
	Abstract Factory class. All factories must inherit from this class.
	"""

	def __init__(self):
		self.fake = Faker()

	@abstractmethod
	def create(self, count=1, **overrides):
		"""
		Method to generate and save fake data.
		Must be implemented by subclasses.
		"""
		pass