from django.test import TestCase

from .models import Region, City


class RegionModelTest(TestCase):

    def test_create_region(self):
        region = Region.objects.create(
            name='Республика Татарстан'
        )
        self.assertEqual(region.name, "Республика Татарстан")
        self.assertIsNotNone(region.id)

class CityModelTest(TestCase):
    #Настройка тестовых данных для проверки связи с регионом
    def setUp(self):
        self.region = Region.objects.create(
            name='Тестовый регион',
        )

    def test_create_city(self):
        city = City.objects.create(
            name='Альметьевск',
            region=self.region,
        )
        self.assertEqual(city.name, 'Альметьевск')
        self.assertEqual(city.region, self.region)

