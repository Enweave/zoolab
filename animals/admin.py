# -*- coding: utf-8 -*-

from django.contrib import admin
from animals.models import AnimalGroup, \
    AnimalType, \
    AnimalNeed, \
    SuppliedAnimal, \
    Supply, \
    ConsumableType, \
    ConsumableGroup, \
    SuppliedConsumable

admin.site.register(AnimalGroup)
admin.site.register(AnimalType)
admin.site.register(AnimalNeed)
admin.site.register(SuppliedConsumable)
admin.site.register(Supply)
admin.site.register(SuppliedAnimal)
admin.site.register(ConsumableGroup)
admin.site.register(ConsumableType)
