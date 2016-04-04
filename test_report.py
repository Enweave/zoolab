# -*- coding: utf-8 -*-

import os
import django
import math

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
import datetime
import time

from animals.models import Supply, SuppliedAnimal, SuppliedConsumable, AnimalNeed, AnimalType

DATEFORMAT = '%d/%m/%Y'


date_from = datetime.datetime.strptime("30/03/2016", DATEFORMAT)
date_to = datetime.datetime.strptime("12/04/2016", DATEFORMAT)
days = (date_to - date_from).days

supplies = list(Supply.objects.filter(date__gte=date_from, date__lte=date_to).order_by("date"))


class ConsumablesStorage(object):
    def __init__(self):
        self.items = {}

    # add new or update existing
    def update_item(self, iid, count):
        existin = self.items.get(iid)
        if existin:
            self.items.update({iid: existin + count})
        else:
            self.items.update({iid: count})

    #decreases existing, returns remaining quantity
    def take_item(self, iid, count):
        existin = self.items.get(iid)
        if existin:
            remainin = existin - count
            self.items.update({iid: remainin})
            return remainin
        else:
            return - count


class AnimalStorage(object):
    def __init__(self):
        self.items = {}

    def update_item(self, iid, type_id, count, needs):
        existin = self.items.get(iid)
        if existin:
            existin.update({"count": existin.get("count") + count})
        else:
            self.items.update({
                iid: {
                    "type_id": type_id,
                    "needs": needs,
                    "count": count
                }
            })


if supplies:
    report = []

    animals = AnimalStorage()
    consumables = ConsumablesStorage()

    def process_phase(supply, span):
        #supply arrived
        for a in SuppliedAnimal.objects.filter(supply=supply):
            animals.update_item(
                "%s%s" % (a.animal_type.id, a.animal_gender),
                a.animal_type.id,
                a.animal_count,
                a.animal_type.get_needs()
            )
        for s in SuppliedConsumable.objects.filter(supply=supply):
            consumables.update_item(s.consumable_type.id, s.consumable_count)

        if span > 0:
        #feeding
            for v in range(0, span):
                for animal in animals.items.values():
                    for need in animal.get("needs"):
                        result = consumables.take_item(
                            need.consumable_type.id,
                            need.consumable_per_day * animal.get("count")
                        )

                        if result < 0:
                            dead_count = math.ceil(float(result) * need.consumable_per_day)
                            report.append((
                                (supply.date + datetime.timedelta(days=v)).strftime(DATEFORMAT),
                                "Погибло %s животных <%s>" % (-dead_count, AnimalType.objects.get(id=animal.get("type_id")))
                            ))
                            animal.update({"count": dead_count if dead_count > 0 else 0})

    for i, c_supply in enumerate(supplies[:-1]):
        c_span = (supplies[i+1].date - c_supply.date).days
        process_phase(c_supply, c_span)

    last_span = (date_to - datetime.datetime.fromordinal(supplies[-1].date.toordinal())).days
    last_supply = supplies[-1]

    process_phase(last_supply, last_span)

    print report