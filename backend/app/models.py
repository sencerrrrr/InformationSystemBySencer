from django.db import models


class Region(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название региона',
        help_text='Введите название региона',
        unique=True,
    )

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название города',
        help_text='Введите название города',
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT, #Защита от удаления региона
        verbose_name='Регион',
        related_name='cities', #Позволит обращаться через region.cities.all()
    )

    def __str__(self):
        return f"{self.name} ({self.region.name})"

