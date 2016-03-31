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

    def __unicode__(self):
        return "Поставка от %s" %  self.date

class SuppliedAnimal(models.Model):
    # TODO: change animal_gender to IntegerField
    GENDERS = (
        (u"male", u"М"),
        (u"female", u"Ж"),
    )

    animal_type = models.ForeignKey(AnimalType, verbose_name=u"Животное")
    animal_count = models.IntegerField(verbose_name=u"Количество")
    animal_gender = models.CharField(choices=GENDERS, max_length=255, verbose_name=u"Пол")
    supply = models.ForeignKey(Supply)

    def get_gender_display(self):
        return next((i[1] for i in self.GENDERS if i[0] == self.animal_gender), None)


class SuppliedConsumable(models.Model):
    consumable_type = models.ForeignKey(ConsumableType, verbose_name="Потребность")
    consumable_count = models.IntegerField(verbose_name=u"Количество")
    supply = models.ForeignKey(Supply)