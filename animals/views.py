# -*- coding: utf-8 -*-
import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from animals.forms import SupplyForm, AddAnimalForm, AddConsumableForm, ReportForm
from animals.models import Supply, AnimalType, AnimalGroup, SuppliedAnimal, SuppliedConsumable, ConsumableType, \
    AnimalNeed
from django.contrib import messages
import datetime
import time
import math

def get_animals(request):
    if request.is_ajax():
        form = AddAnimalForm()
        item_name = u'Животное'
        html = render_to_string("common/widgets/supplies_fieldset.html", locals())
        return JsonResponse({"html": html})
    return HttpResponseRedirect("/")


def get_consumables(request):
    if request.is_ajax():
        form = AddConsumableForm()
        item_name = u'Потребность'
        html = render_to_string("common/widgets/supplies_fieldset.html", locals())
        return JsonResponse({"html": html})
    return HttpResponseRedirect("/")


def supplies_page(request):
    nav_selected = 0
    supplies = Supply.objects.all().order_by("-date")

    form = SupplyForm()
    if request.POST:
        form = SupplyForm(request.POST)
        if form.is_valid():
            grouped_animal_types = {}
            for i, animal_type in enumerate(request.POST.getlist("animal_type", ())):
                gender = request.POST.getlist("animal_gender")[i]
                count = int(request.POST.getlist("animal_count")[i])

                group_id = "%s%s" % (animal_type, gender)

                current_group = grouped_animal_types.get(group_id, {
                    "type": animal_type,
                    "gender": gender,
                })
                current_group.update({"count": count + current_group.get("count", 0)})

                grouped_animal_types.update({group_id: current_group})

            consumables = []
            for i, consumble_type in enumerate(request.POST.getlist("consumable_type", ())):
                consumables.append({"type": consumble_type, "count": int(request.POST.getlist("consumable_count")[i])})

            if grouped_animal_types or consumables:
                new_supply = Supply(**form.cleaned_data)
                new_supply.save()
                for supplied_animal in grouped_animal_types.values():
                    new_supplied_animal = SuppliedAnimal(
                        supply=new_supply,
                        animal_type=AnimalType.objects.get(id=supplied_animal["type"]),
                        animal_count=supplied_animal["count"],
                        animal_gender=supplied_animal["gender"]
                    )
                    new_supplied_animal.save()
                for consumable in consumables:

                    new_supplied_consumable = SuppliedConsumable(
                        supply=new_supply,
                        consumable_type=ConsumableType.objects.get(id=consumable["type"]),
                        consumable_count=consumable["count"]
                    )
                    new_supplied_consumable.save()
                messages.success(request, u"Успешно добавлена %s" % new_supply)
            return HttpResponseRedirect(reverse('animals:supplies'))
    return render(request, "common/supplies.html", locals())


def remove_supply(request, pk):
    if request.POST and request.is_ajax():
        supplies = Supply.objects.filter(id=pk)
        if supplies:
            if request.POST.get("confirm"):
                supplies[0].delete()
                return JsonResponse({"success": True})
            return JsonResponse({"success": False})
        else:
            return JsonResponse({"success": False})

    return HttpResponseRedirect("/")



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
            self.items.update({iid: remainin if remainin > 0 else 0})
            return remainin
        else:
            return -count


class AnimalStorage(object):
    def __init__(self):
        self.items = {}

    def append_item(self, iid, name, count, needs, is_female=False):
        existin = self.items.get(iid)
        if existin:
            existin.update({
                "count": existin.get("count") + count,
            })
            if is_female:
                existin.update({
                    "female_count": existin.get("female_count") + count
                })
        else:
            self.items.update({
                iid: {
                    "name": name,
                    "needs": needs,
                    "count": count,
                    "female_count": count if is_female else 0,
                    "breed_rate": 1,
                }
            })

    def die(self, iid, count):
        existin = self.items.get(iid)
        if existin:
            result_count = existin.get("count") - count
            existin.update({
                "count": result_count if result_count > 0 else 0,
            })

def reports_page(request):
    DATEFORMAT = '%d/%m/%Y'
    nav_selected = 1
    report_form = ReportForm()
    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            gender_female = SuppliedAnimal.GENDERS[1][0]
            date_to = report_form.cleaned_data.get("date_to")

            supplies = list(Supply.objects.filter(date__lte=date_to))
            if supplies:
                report = []

                animals = AnimalStorage()
                consumables = ConsumablesStorage()

                def process_phase(supply, span):
                    #supply arrived
                    for a in SuppliedAnimal.objects.filter(supply=supply):
                        animals.append_item(
                            a.animal_type.id,
                            a.animal_type.name,
                            a.animal_count,
                            a.animal_type.get_needs(),
                            a.animal_gender == gender_female
                        )
                    for s in SuppliedConsumable.objects.filter(supply=supply):
                        consumables.update_item(s.consumable_type.id, s.consumable_count)

                    if span > 0:
                    #feeding
                        for v in range(0, span):
                            for aiid, animal in animals.items.iteritems():
                                lowest_efficiency = 0
                                highest_need = None
                                for need in animal.get("needs"):
                                    current_animal_count = animal.get("count")
                                    if current_animal_count > 0:
                                        efficiency = consumables.take_item(
                                            need.consumable_type.id,
                                            need.consumable_per_day * current_animal_count
                                        )
                                        if efficiency < lowest_efficiency:
                                            lowest_efficiency = efficiency
                                            highest_need = need
                                if lowest_efficiency < 0:
                                    dead_count = -int(math.ceil(float(lowest_efficiency) * highest_need.consumable_per_day))
                                    animals.die(aiid, dead_count)

                    #TODO: breeding
                for i, c_supply in enumerate(supplies[:-1]):
                    c_span = (supplies[i+1].date - c_supply.date).days
                    process_phase(c_supply, c_span)

                last_span = (date_to - supplies[-1].date).days
                last_supply = supplies[-1]
                process_phase(last_supply, last_span)

                print animals.items.values()

    return render(request, "common/reports.html", locals())
