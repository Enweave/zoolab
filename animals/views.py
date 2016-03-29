# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from animals.forms import SupplyForm
from animals.models import Supply


def supplies_page(request):
    nav_selected = 0
    supplies = Supply.objects.all()

    form = SupplyForm()

    if request.POST:
        form = SupplyForm(request.POST)
    return render(request, "common/supplies.html", locals())


def reports_page(request):
    nav_selected = 1
    return render(request, "common/reports.html", locals())
