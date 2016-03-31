# -*- coding: utf-8 -*-
import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from animals.forms import SupplyForm, AddAnimalForm, AddConsumableForm
from animals.models import Supply, AnimalType, AnimalGroup, SuppliedAnimal, SuppliedConsumable, ConsumableType
from django.contrib import messages

def get_animals(request):
    form = AddAnimalForm()
    html = render_to_string("common/widgets/animal_types.html", locals())
    return JsonResponse({"html": html})


def get_consumables(request):
    form = AddConsumableForm()
    html = render_to_string("common/widgets/consumable_types.html", locals())
    return JsonResponse({"html": html})


def supplies_page(request):
    nav_selected = 0
    supplies = Supply.objects.all()

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


def reports_page(request):
    nav_selected = 1
    return render(request, "common/reports.html", locals())
