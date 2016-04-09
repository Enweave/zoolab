# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class AnimalGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Название")

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = u"Группа животных"
        verbose_name_plural = u"Группы животных"


class AnimalType(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Название")
    group = models.ForeignKey(AnimalGroup, verbose_name=u"Группа животных")

    def __unicode__(self):
        return u"%s" % self.name

    #Получить потребности для данного типа животного
    def get_needs(self):
        return AnimalNeed.objects.filter(animal_type=self)

    class Meta:
        verbose_name = u"Тип животного"
        verbose_name_plural = u"Типы животных"


class ConsumableGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Название")

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = u"Тип животного"
        verbose_name_plural = u"Типы животных"


class ConsumableType(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Название")
    group = models.ForeignKey(ConsumableGroup, verbose_name=u"Группа потребностей")

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = u"Тип потребности"
        verbose_name_plural = u"Типы потребностей"


class AnimalNeed(models.Model):
    """
        Служебный класс,
        используется для того, чтобы установить, сколько тип животного потребляет в день
        потребность определённого типа
    """
    animal_type = models.ForeignKey(AnimalType, verbose_name=u"Тип животного")
    consumable_per_day = models.IntegerField(verbose_name=u"Потребляется в день")
    consumable_type = models.ForeignKey(ConsumableType, verbose_name=u"Тип потребности")

    def __unicode__(self):
        return u"потребность <%s> в <%s> - %s " % (self.animal_type, self.consumable_type, self.consumable_per_day)

    class Meta:
        verbose_name = u"Потребность животного"
        verbose_name_plural = u"Потребность животных"


class Supply(models.Model):
    date = models.DateField(verbose_name="Дата поставки")
    comment = models.TextField(blank=True, null=True, verbose_name=u"Комментарий")

    #Получить всех животных в данной поставке
    def get_animals(self):
        return SuppliedAnimal.objects.filter(supply=self)

    #Получить все потребности в данной поставке
    def get_consumables(self):
        return SuppliedConsumable.objects.filter(supply=self)

    def __unicode__(self):
        return "Поставка от %s" % self.date


class SuppliedAnimal(models.Model):
    """
    Служебный класс,
    показывает, сколько животных конкретного типа и какого пола было добавлено с указанной поставкой
    """
    GENDERS = (
        (u"male", u"М"),
        (u"female", u"Ж"),
    )

    animal_type = models.ForeignKey(AnimalType, verbose_name=u"Тип животного")
    animal_count = models.IntegerField(verbose_name=u"Количество")
    animal_gender = models.CharField(choices=GENDERS, max_length=255, verbose_name=u"Пол животного")
    supply = models.ForeignKey(Supply)

    def get_gender_display(self):
        return next((i[1] for i in self.GENDERS if i[0] == self.animal_gender), None)

    def __unicode__(self):
        return u"%s %s x %s" % (self.animal_type, self.get_gender_display(), self.animal_count)


class SuppliedConsumable(models.Model):
    """
    Служебный класс,
    показывает, сколько животных конкретного типа и какого пола было добавлено с указанной поставкой
    """
    consumable_type = models.ForeignKey(ConsumableType, verbose_name=u"Тип потребности")
    consumable_count = models.IntegerField(verbose_name=u"Количество")
    supply = models.ForeignKey(Supply)

    def __unicode__(self):
        return u"%s x %s" % (self.consumable_type.name, self.consumable_count)
