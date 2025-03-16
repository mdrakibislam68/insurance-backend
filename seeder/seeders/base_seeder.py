from abc import ABC, abstractmethod

class BaseSeeder(ABC):
    """
    Abstract Seeder class. All seeders must inherit from this class.
    """

    @abstractmethod
    def run(self):
        """
        Method to run the seeder.
        Must be implemented by subclasses.
        """
        pass