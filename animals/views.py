# -*- coding: utf-8 -*-
import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from animals.forms import SupplyForm, AddAnimalForm, AddConsumableForm, ReportForm
from animals.models import Supply, AnimalType, AnimalGroup, SuppliedAnimal, SuppliedConsumable, ConsumableType
from django.contrib import messages


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


def reports_page(request):
    nav_selected = 1
    report_form = ReportForm()
    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            date_from = report_form.cleaned_data.get("date_from")
            date_to = report_form.cleaned_data.get("date_to")
            days = (date_to - date_from).days

            supplies = Supply.objects.filter(date__gte=date_from, date__lte=date_to)
            if supplies:
                animals = SuppliedAnimal.objects.filter(supply__in=supplies)
                consumables = SuppliedConsumable.objects.filter(supply__in=supplies)
    return render(request, "common/reports.html", locals())
