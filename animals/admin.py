# -*- coding: utf-8 -*-

from django.contrib import admin
from animals.models import AnimalGroup
from animals.models import AnimalType
from animals.models import AnimalNeed
from animals.models import ConsumableType
from animals.models import ConsumableGroup


class AnimalGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(AnimalGroup, AnimalGroupAdmin)


class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ('name', "group")


admin.site.register(AnimalType, AnimalTypeAdmin)


class ConsumableGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ConsumableGroup, ConsumableGroupAdmin)


class ConsumableTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')


admin.site.register(ConsumableType, ConsumableTypeAdmin)


class AnimalNeedAdmin(admin.ModelAdmin):
    list_display = ('animal_type', 'consumable_type', 'consumable_per_day')
    list_editable = ('consumable_type', 'consumable_per_day',)


admin.site.register(AnimalNeed, AnimalNeedAdmin)

