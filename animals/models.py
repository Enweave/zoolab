# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class AnimalGroup(models.Model):
    name = models.CharField(max_length=255)


class AnimalType(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(AnimalGroup)


class ConsumableGroup(models.Model):
    name = models.CharField(max_length=255)


class ConsumableType(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(ConsumableGroup)


class AnimalNeed(models.Model):
    animal_type = models.ForeignKey(AnimalType)
    consumable_per_day = models.IntegerField()
    consumable_type = models.ForeignKey(ConsumableType)


class Supply(models.Model):
    date = models.DateField()
    comment = models.TextField(blank=True, null=True)


class SuppliedAnimal(models.Model):
    GENDERS = (
        (0, u"male"),
        (1, u"female"),
    )

    animal_type = models.ForeignKey(AnimalType)
    animal_count = models.IntegerField()
    animal_gender = models.CharField(choices=GENDERS, max_length=255)
    supply = models.ForeignKey(Supply)


class SuppliedConsumable(models.Model):
    consumable_type = models.ForeignKey(ConsumableType)
    consumable_count = models.IntegerField()
    supply = models.ForeignKey(Supply)