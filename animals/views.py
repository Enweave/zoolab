# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect

from django.shortcuts import render
from django.template.loader import render_to_string
from animals.forms import SupplyForm, AddAnimalForm, AddConsumableForm, ReportForm, get_input_date_format
from animals.models import Supply, AnimalType, SuppliedAnimal, SuppliedConsumable, ConsumableType
from django.contrib import messages
import datetime
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


def add_report_row(date, animal_name, count):
    return {
        "date": date,
        "content": "%s x %s" % (animal_name, count)
    }


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

    def die(self, iid, count, date):
        existin = self.items.get(iid)
        deaths = []
        if existin:
            result_count = existin.get("count") - count
            result_count = result_count if result_count > 0 else 0

            female_count = existin.get("female_count")
            result_female_count = result_count/2
            existin.update({
                "count": result_count if result_count > 0 else 0,
                "female_count": result_female_count if result_female_count < female_count else female_count
            })
            deaths.append(add_report_row(date, existin.get("name"), count))
        return deaths

    def breed(self, date=None):
        new_ones = []
        for item in self.items.values():
            pairs = min([item.get("count") - item.get("female_count"), item.get("female_count")])
            new_breed = int(math.floor(pairs*item.get("breed_rate")))
            item.update({
                "count": item.get("count") + new_breed,
                "female_count": item.get("female_count") + new_breed/2
            })
            if new_breed > 0:
                new_ones.append(add_report_row(date, item.get("name"), new_breed))
        return new_ones


def reports_page(request):
    DATEFORMAT = get_input_date_format()
    nav_selected = 1
    report_form = ReportForm()

    recommendations = []
    deaths = []
    spawns = []

    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            has_report = True
            gender_female = SuppliedAnimal.GENDERS[1][0]

            date_to = report_form.cleaned_data.get("date_to")
            selected_animal_group_id = report_form.cleaned_data.get("group")
            spawn = report_form.cleaned_data.get("spawn")
            supplies = list(Supply.objects.filter(date__lte=date_to).order_by("date"))
            if supplies:


                animals = AnimalStorage()
                consumables = ConsumablesStorage()

                def make_report_row(date, consumable_name, count):
                    return {
                        "date": date,
                        "content": "%s x %s" % (consumable_name, count)
                    }

                def process_phase(supply, span):
                    #supply arrived
                    for a in SuppliedAnimal.objects.filter(supply=supply, animal_type__id=selected_animal_group_id):
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

                        for v in range(0, span):
                            report_entry_date = (supply.date + datetime.timedelta(days=v)).strftime(DATEFORMAT)
                            #feeding

                            for aiid, animal in animals.items.iteritems():
                                lowest_efficiency = 0
                                highest_need = None
                                current_animal_count = animal.get("count")
                                for need in animal.get("needs"):
                                    if current_animal_count > 0:
                                        efficiency = consumables.take_item(
                                            need.consumable_type.id,
                                            need.consumable_per_day * current_animal_count
                                        )
                                        if efficiency < lowest_efficiency:
                                            lowest_efficiency = efficiency
                                            highest_need = need
                                        if efficiency < 0:
                                            recommendations.append(add_report_row(
                                                report_entry_date,
                                                need.consumable_type.name,
                                                -efficiency,
                                            ))
                                if lowest_efficiency < 0 < current_animal_count:
                                    dead_count = -int(math.ceil(float(lowest_efficiency) * highest_need.consumable_per_day))
                                    new_deaths = animals.die(aiid, dead_count, report_entry_date)
                                    for d in new_deaths:
                                        deaths.append(d)
                            #breeding
                            if spawn:
                                new_spawns = animals.breed(report_entry_date)
                                for n in new_spawns:
                                    spawns.append(n)

                for i, c_supply in enumerate(supplies[:-1]):
                    c_span = (supplies[i+1].date - c_supply.date).days
                    process_phase(c_supply, c_span)

                last_span = (date_to - supplies[-1].date).days
                last_supply = supplies[-1]
                process_phase(last_supply, last_span)
    return render(request, "common/reports.html", locals())
