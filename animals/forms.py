# -*- coding: utf-8 -*-

from models import Supply
from django import forms


class SupplyForm(forms.Form):
    BASE_ATTRS = {"class": "form-control"}
    date = forms.DateField(widget=forms.DateInput(attrs={"class": "form-control"}))
    comment = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 3,
    }))

    animals = forms.CharField(widget=forms.HiddenInput())
    # consumables = forms.HiddenInput()

    # class Meta:
    #     model = Supply
    #     exclude = ()