from django.shortcuts import render

from django.http import HttpResponse
from .models import Region, City


def check_data(request):
    """Временный view для проверки данных"""
    output = []

    output.append("<h1>Проверка данных в базе</h1>")

    # Счетчики
    output.append(f"<p>Регионов: {Region.objects.count()}</p>")
    output.append(f"<p>Городов: {City.objects.count()}</p>")

    # Список регионов и городов
    output.append("<h2>Регионы и города:</h2>")
    for region in Region.objects.all().order_by('name'):
        cities = region.cities.all()
        city_list = ", ".join([city.name for city in cities])
        output.append(f"<p><b>{region.name}</b>: {city_list}</p>")

    return HttpResponse("\n".join(output))
