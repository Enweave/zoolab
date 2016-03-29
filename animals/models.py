# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class AnimalGroup(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % self.name

    # @models.permalink
    # def get_absolute_url(self):
    #     return 'animals:animal-group-detail', (), {'pk': self.id}


class AnimalType(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(AnimalGroup)

    def __unicode__(self):
        return u"%s" % self.name


class ConsumableGroup(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % self.name


class ConsumableType(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(ConsumableGroup)

    def __unicode__(self):
        return u"%s" % self.name


class AnimalNeed(models.Model):
    animal_type = models.ForeignKey(AnimalType)
    consumable_per_day = models.IntegerField()
    consumable_type = models.ForeignKey(ConsumableType)


class Supply(models.Model):
    date = models.DateField()
    comment = models.TextField(blank=True, null=True)

    def get_animals(self):
        return SuppliedAnimal.objects.filter(supply=self)

    def get_consumables(self):
        return SuppliedConsumable.objects.filter(supply=self)


class SuppliedAnimal(models.Model):
    # TODO: change animal_gender to IntegerField
    GENDERS = (
        (u"male", u"male"),
        (u"female", u"female"),
    )

    animal_type = models.ForeignKey(AnimalType)
    animal_count = models.IntegerField()
    animal_gender = models.CharField(choices=GENDERS, max_length=255)
    supply = models.ForeignKey(Supply)


class SuppliedConsumable(models.Model):
    consumable_type = models.ForeignKey(ConsumableType)
    consumable_count = models.IntegerField()
    supply = models.ForeignKey(Supply)